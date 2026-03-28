from env.environment import ClinicalTrialEnvironment
from env.models import Action
from tasks.definitions import TASKS


def test_task(task_id):
    env = ClinicalTrialEnvironment()
    obs = env.reset(task_id)
    assert obs.remaining == len(TASKS[task_id]['patients'])

    total = 0.0
    while True:
        # baseline heuristic: follow nominal correct by reusing env private method
        patient = env.patients[env.index]
        expected = env._correct_action(patient)
        action = Action(decision=expected, rationale='test')
        obs, reward, done, info = env.step(action)
        total += reward.value
        if done:
            break

    assert 0.0 <= total <= len(TASKS[task_id]['patients']) * 2.0
    # Last state should show done
    st = env.state()
    assert st['index'] == len(TASKS[task_id]['patients'])


if __name__ == '__main__':
    for tid in ['easy', 'medium', 'hard']:
        test_task(tid)
    print('OK')
