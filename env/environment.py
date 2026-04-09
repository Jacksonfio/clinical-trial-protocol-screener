from .models import Observation, Action, Reward, Patient, Protocol
from tasks.definitions import TASKS
from typing import Optional

class ClinicalTrialEnvironment:
    def __init__(self):
        self.task_id: Optional[str] = None
        self.protocol: Optional[Protocol] = None
        self.patients: list[Patient] = []
        self.index = 0
        self.decisions: list[Action] = []

    def reset(self, task_id: str = 'easy') -> Observation:
        task = TASKS.get(task_id)
        if task is None:
            raise ValueError(f"Unknown task_id '{task_id}'")
        self.task_id = task_id
        self.protocol = task['protocol']
        self.patients = task['patients']
        self.index = 0
        self.decisions = []
        return self._make_observation()

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict]:
        if self.index >= len(self.patients):
            raise RuntimeError("Episode is already done")

        self.decisions.append(action)
        patient = self.patients[self.index]
        score, details = self._score_action(patient, action)
        self.index += 1

        done = self.index >= len(self.patients)
        obs = self._make_observation() if not done else Observation(
            protocol_id=self.protocol.id,
            protocol_name=self.protocol.name,
            patient=patient,
            remaining=0
        )
        reward = Reward(value=score, details=details)
        info = {'current_index': self.index, 'done': done, 'task_id': self.task_id}
        return obs, reward, done, info

    def state(self) -> dict:
        return {
            'task_id': self.task_id,
            'protocol_id': self.protocol.id if self.protocol else None,
            'index': self.index,
            'total': len(self.patients),
            'decisions': [d.dict() for d in self.decisions],
        }

    def _make_observation(self) -> Observation:
        patient = self.patients[self.index]
        return Observation(
            protocol_id=self.protocol.id,
            protocol_name=self.protocol.name,
            patient=patient,
            remaining=len(self.patients) - self.index
        )

    def _score_action(self, patient: Patient, action: Action) -> tuple[float, dict]:
        correct = self._correct_action(patient)
        if action.decision == correct:
            base = 1.0
        elif action.decision == 'request_more_info':
            base = 0.2
        elif action.decision == 'approve' and correct == 'reject':
            base = -0.5  # Asymmetric penalty for safety violation
        else:
            base = 0.0

        # partial credit for flagging obvious exclusion or inclusion pieces
        partial = 0.0
        if 'diabetes' in patient.conditions and 'diabetes' in self.protocol.exclusion:
            partial = 0.25
        if patient.consent_signed:
            partial += 0.25

        return min(1.0, base + partial), {'expected': correct, 'partial': partial}

    def _correct_action(self, patient: Patient) -> str:
        if not patient.consent_signed:
            return 'reject'

        for excl in self.protocol.exclusion:
            if excl in patient.conditions:
                return 'reject'

        for lab, bounds in self.protocol.required_labs.items():
            if lab not in patient.labs:
                return 'request_more_info'
            value = patient.labs[lab]
            if not (bounds['min'] <= value <= bounds['max']):
                return 'reject'

        for med in self.protocol.banned_medications:
            if med in patient.medications:
                return 'reject'

        if self.protocol.inclusion:
            for inc in self.protocol.inclusion:
                if inc not in patient.conditions:
                    return 'reject'

        return 'approve'
