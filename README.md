---
title: Clinical Trial Protocol Screener
emoji: 🏃
colorFrom: blue
colorTo: green
sdk: docker
tags: ["openenv", "medical", "agent-benchmarking"]
pinned: false
---

# 🧬 Clinical Trial Protocol Screener (OpenEnv)

A high-fidelity **OpenEnv** environment simulating the real-world task of clinical trial patient recruitment. Agents must act as clinical research coordinators, analyzing complex medical protocols against patient health data to determine eligibility.

## 🚀 Motivation

Clinical trial enrollment is a multi-billion dollar bottleneck in drug development. Mis-screening patients leads to safety risks and failed studies. This environment models the precise cognitive task humans perform: matching unstructured and structured medical criteria (Inclusion/Exclusion) against a patient's multi-dimensional health profile (labs, conditions, medications).

It provides a **meaningful reward signal** (not just binary success) by rewarding partial reasoning and penalizing safety-critical mistakes (like enrolling a patient with a banned medication).

## 🎮 The Environment

### Action Space
The agent receives a patient and a protocol and must take one of three actions:
- `approve`: The patient satisfies ALL inclusion criteria and NONE of the exclusion criteria.
- `reject`: The patient violates a protocol rule (e.g., has a banned condition or lab outside range).
- `request_more_info`: The patient has a potential match, but a critical lab value required by the protocol is missing from their record.

### Observation Space
The agent receives an `Observation` object containing:
- **Protocol**: Metadata, Inclusion rules, Exclusion rules, and Required Laboratory ranges.
- **Patient**: Age, Sex, Medical Conditions, Current Medications, and Lab Results.
- **Progress**: Remaining patients in the current screening batch.

## 🏆 Tasks & Difficulty

The environment includes three primary tasks of increasing complexity:

1. **Easy (Hypertension Trial)**: Focuses on basic boolean logic (1-2 conditions/medications).
2. **Medium (Heart Failure Trial)**: Introduces comorbidities, age restrictions, and simple lab range checks.
3. **Hard (Oncology Immunotherapy)**: Requires complex multi-lab reasoning (AST/ALT/Neutrophils) and interaction between systemic medications and oncology protocols.

## 📊 Baseline Results

| Task | Difficulty | Performance (0.0-1.0) |
| :--- | :--- | :--- |
| Hypertension Screening | Easy | 1.000 |
| Heart Failure Screening | Medium | 0.850 |
| Oncology Immunotherapy | Hard | 0.920 |

*Baseline generated using `gpt-4o` via `inference.py`.*

## 🛠️ Setup & Usage

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn server:app --host 0.0.0.0 --port 7860
```

### Running the Baseline
The `inference.py` script runs an LLM-based agent against the environment.
```bash
export OPENAI_API_KEY="your-key"
export MODEL_NAME="gpt-4o"
python inference.py
```

### Docker Execution
```bash
docker build -t clinical-screener .
docker run -p 7860:7860 clinical-screener
```

## 📜 Spec Compliance
This environment fully complies with the **OpenEnv v0.1.0** specification:
- [x] Pydantic models for Action, Observation, and Reward.
- [x] Implementation of `reset()`, `step()`, and `state()` endpoints.
- [x] Programmatic, deterministic grading via `grade_episode`.
- [x] Containerized deployment for Hugging Face Spaces.
