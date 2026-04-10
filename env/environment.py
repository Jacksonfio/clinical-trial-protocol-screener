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
            raise ValueError(f"Unknown task_id '{task_id}'. Valid: {list(TASKS.keys())}")
        self.task_id = task_id
        self.protocol = task['protocol']
        self.patients = task['patients']
        self.index = 0
        self.decisions = []
        return self._make_observation()

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict]:
        if self.index >= len(self.patients):
            raise RuntimeError("Episode is already done. Call reset() to start a new episode.")

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
            # Partial credit for expressing uncertainty (better than a wrong decisive action)
            base = 0.2
        elif action.decision == 'approve' and correct == 'reject':
            # SAFETY VIOLATION: Approving a patient who should be rejected
            # Asymmetric hard penalty — closely mirrors real-world medical ethics
            base = -0.5
        else:
            # Incorrect rejection (false negative) — lost enrollment opportunity
            base = 0.0

        # ── Partial credit bonuses ──────────────────────────────────────────
        partial = 0.0

        # Reward for correctly flagging a diabetes exclusion (common safety signal)
        if ('diabetes' in patient.conditions and
                'diabetes' in self.protocol.exclusion):
            partial = 0.25

        # Reward for noting consent is signed (administrative diligence signal)
        if patient.consent_signed:
            partial += 0.25

        final_score = min(1.0, base + partial)
        # Clamp strictly within (0, 1) to satisfy OpenEnv bounds
        final_score = max(0.001, min(0.999, final_score))

        return final_score, {
            'expected': correct,
            'got': action.decision,
            'partial_bonus': partial,
            'safety_violation': action.decision == 'approve' and correct == 'reject',
        }

    def _correct_action(self, patient: Patient) -> str:
        """
        Deterministically compute the correct decision for a patient.
        Evaluation order (mirrors real clinical protocol screening):
        1. Consent check
        2. Explicit exclusion conditions
        3. Drug-drug interactions (novel: checks dangerous medication pairs)
        4. Required lab bounds (missing lab → request_more_info; out of range → reject)
        5. Implicit lab-based exclusion (expert-level: must infer condition from lab value)
        6. Banned medications
        7. Inclusion criteria
        """

        # 1. Consent
        if not patient.consent_signed:
            return 'reject'

        # 2. Explicit exclusion conditions
        for excl in self.protocol.exclusion:
            if excl in patient.conditions:
                return 'reject'

        # 3. Drug-drug interactions — checks if any dangerous medication PAIR is present
        for pair in self.protocol.drug_interactions:
            if all(drug in patient.medications for drug in pair):
                return 'reject'

        # 4. Required lab bounds
        for lab, bounds in self.protocol.required_labs.items():
            if lab not in patient.labs:
                return 'request_more_info'
            value = patient.labs[lab]
            if not (bounds['min'] <= value <= bounds['max']):
                return 'reject'

        # 5. Implicit lab-based exclusion (EXPERT LEVEL)
        # The exclusion condition name is never given — the agent must infer it from the raw value
        # e.g. eGFR=22 → implies "severe renal impairment" even without naming it
        for lab, threshold in self.protocol.implicit_exclusion_labs.items():
            if lab in patient.labs:
                if 'max_for_exclusion' in threshold:
                    if patient.labs[lab] < threshold['max_for_exclusion']:
                        return 'reject'
                if 'min_for_exclusion' in threshold:
                    if patient.labs[lab] > threshold['min_for_exclusion']:
                        return 'reject'

        # 6. Banned medications
        for med in self.protocol.banned_medications:
            if med in patient.medications:
                return 'reject'

        # 7. Inclusion criteria (all must be present)
        for inc in self.protocol.inclusion:
            if inc not in patient.conditions:
                return 'reject'

        return 'approve'
