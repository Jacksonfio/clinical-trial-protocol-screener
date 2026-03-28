from fastapi import FastAPI, HTTPException
from typing import Optional
from env.environment import ClinicalTrialEnvironment
from env.models import Action, Observation, Reward
from tasks.definitions import TASKS
from graders.reward import grade_episode
from baseline.inference import run_baseline

app = FastAPI(title='Clinical Trial Screener OpenEnv')

env = ClinicalTrialEnvironment()

from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Docs",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

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
