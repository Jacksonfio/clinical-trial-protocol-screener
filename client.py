from env.environment import ClinicalTrialEnvironment
from env.models import Observation, Action, Reward
from typing import Tuple, Dict, Any

class OpenEnvClient:
    def __init__(self):
        self.env = ClinicalTrialEnvironment()

    def reset(self, task_id: str = 'easy') -> Observation:
        return self.env.reset(task_id)

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        return self.env.step(action)

    def state(self) -> Dict[str, Any]:
        return self.env.state()
