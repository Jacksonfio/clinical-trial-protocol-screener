from fastapi import FastAPI, HTTPException
from typing import Optional
from env.environment import ClinicalTrialEnvironment
from env.models import Action, Observation, Reward
from tasks.definitions import TASKS
from graders.reward import grade_episode
# from baseline.inference import run_baseline (Removed to avoid startup overhead)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='clinical-trial-protocol-screener')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = ClinicalTrialEnvironment()

@app.get('/')
def root():
    return {"status": "ok", "framework": "openenv"}

@app.get('/health')
def health():
    return {"status": "healthy"}

@app.get('/metadata')
def metadata():
    return {
        "name": "clinical-trial-protocol-screener",
        "description": "A high-fidelity Clinical Trial Screening environment for testing medical decision-making agents.",
        "version": "0.1.0",
        "framework": "openenv"
    }

@app.get('/schema')
def schema():
    return {
        "action": {
            "type": "object",
            "properties": {
                "decision": {"type": "string", "enum": ["approve", "reject", "request_more_info"]},
                "rationale": {"type": "string"}
            },
            "required": ["decision", "rationale"]
        },
        "observation": {
            "type": "object",
            "properties": {
                "protocol_id": {"type": "string"},
                "protocol_name": {"type": "string"},
                "patient": {"type": "object"},
                "remaining": {"type": "integer"}
            }
        },
        "state": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "index": {"type": "integer"},
                "total": {"type": "integer"},
                "decisions": {"type": "array"}
            }
        }
    }

@app.post('/mcp')
def mcp():
    return {"jsonrpc": "2.0", "result": {"name": "clinical-trial-protocol-screener"}, "id": None}

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
    return {"status": "Baseline script is located at the root of the repository as 'inference.py' and should be run directly."}
