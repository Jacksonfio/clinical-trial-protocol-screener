import os
import time
from env.environment import ClinicalTrialEnvironment
from env.models import Action

try:
    import openai
except ImportError:
    openai = None


def rule_agent(obs):
    p = obs.patient
    # simple logic just to run a baseline
    if not p.consent_signed:
        return 'reject'
    if 'autoimmune_disease' in p.conditions or 'diabetes' in p.conditions:
        return 'reject'
    if any(m in p.medications for m in ['warfarin', 'amiodarone', 'systemic_steroids']):
        return 'reject'
    return 'approve'


def run_baseline():
    env = ClinicalTrialEnvironment()
    results = {}
    for task_id in ['easy', 'medium', 'hard']:
        obs = env.reset(task_id)
        total_reward = 0.0
        done = False
        while not done:
            action = Action(decision=rule_agent(obs), rationale='rule-based')
            obs, reward, done, _ = env.step(action)
            total_reward += reward.value
        results[task_id] = {'episode_reward': total_reward, 'grader': env._score_action}

    return results

if __name__ == '__main__':
    out = run_baseline()
    import json
    print(json.dumps(out, indent=2))
