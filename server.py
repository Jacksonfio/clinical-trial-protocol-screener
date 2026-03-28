from fastapi import FastAPI, HTTPException
from typing import Optional
from env.environment import ClinicalTrialEnvironment
from env.models import Action, Observation, Reward
from tasks.definitions import TASKS
from graders.reward import grade_episode
from baseline.inference import run_baseline

app = FastAPI(title='Clinical Trial Screener OpenEnv')

env = ClinicalTrialEnvironment()

@app.get('/tasks')
def list_tasks():
    return {k: {'protocol_id': v['protocol'].id, 'name': v['protocol'].name, 'num_patients': len(v['patients'])} for k, v in TASKS.items()}

@app.post('/reset')
def reset(task_id: Optional[str] = 'easy'):
    try:
        obs = env.reset(task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return obs

@app.post('/step')
def step(action: Action):
    try:
        obs, reward, done, info = env.step(action)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        'observation': obs,
        'reward': reward,
        'done': done,
        'info': info,
    }

@app.get('/state')
def state():
    return env.state()

@app.get('/grader')
def grader():
    return grade_episode(env)

@app.get('/baseline')
def baseline():
    return run_baseline()
