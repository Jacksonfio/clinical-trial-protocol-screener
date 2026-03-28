# Clinical Trial Protocol Screener

A real-world OpenEnv environment where an agent screens candidate patients for clinical trials.

## Environment

- 3 tasks: easy/medium/hard
- Implemented API: reset(), step(action), state()
- Grader returns score 0.0..1.0

## API

- GET /tasks - List all tasks
- POST /reset?task_id=<easy|medium|hard> - Reset environment
- POST /step - Execute action
- GET /state - Get current state
- GET /grader - Get final score
- GET /baseline - Run baseline agent

## Task Overview

- **Easy**: 3 patients, hypertension trial screening
- **Medium**: Heart failure trial with comorbidities and age rules
- **Hard**: Oncology immunotherapy with lab value ranges

## Installation

```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 7860
```

## Baseline Scores

- Easy: 3.0/3.0
- Medium: 2.25/3.0  
- Hard: 3.0/3.0

## Testing

```bash
python tests/validate_logic.py
```
