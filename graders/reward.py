from env.environment import ClinicalTrialEnvironment
from env.models import Action


def grade_episode(env: ClinicalTrialEnvironment) -> dict:
    if not env.task_id:
        raise ValueError('Environment not initialized')
    decisions = env.decisions
    if not decisions:
        return {'score': 0.0, 'details': 'No decisions made'}

    # Fake final summary: normalized average of reward guesses
    total = 0.0
    for i, decision in enumerate(decisions):
        patient = env.patients[i]
        correct = env._correct_action(patient)
        if decision.decision == correct:
            total += 1.0
        elif decision.decision == 'request_more_info':
            total += 0.2
    score = total / len(decisions)
    # OpenEnv requires score strictly in (0, 1)
    score = max(0.001, min(0.999, score))
    return {'score': round(score, 4), 'n': len(decisions)}
