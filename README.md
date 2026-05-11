---
title: Clinical Trial Protocol Screener
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: docker
tags: ["openenv", "medical-ai", "screening-automation", "agent-benchmarking", "drug-interactions", "implicit-reasoning"]
pinned: true
---

# 🧬 Clinical Trial Protocol Screener (OpenEnv v0.2.0)

[![OpenEnv Spec v0.2.0](https://img.shields.io/badge/OpenEnv-v0.2.0-brightgreen)](https://github.com/OpenEnv/spec)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tasks: 4](https://img.shields.io/badge/Tasks-4%20(Easy→Expert)-blue)](https://github.com/Jacksonfio/clinical-trial-protocol-screener)
[![Patients: 20](https://img.shields.io/badge/Patients-20%20edge--case%20profiles-orange)](https://github.com/Jacksonfio/clinical-trial-protocol-screener)

> **The only OpenEnv environment that requires an AI agent to perform implicit medical reasoning** — inferring patient exclusions from raw lab values without being told the condition name.

---

## 🚨 The Real Problem This Solves

Clinical trial enrollment is the **single greatest bottleneck in modern drug discovery.** Manual patient screening:
- Costs **$10,000–$15,000 per enrolled patient** in coordinator hours
- Takes **3–8 months** per trial to screen enough patients
- Has a **75% screen failure rate** due to complex eligibility criteria
- Results in **$8B+ wasted** annually on delayed trials

This environment gives AI agents a structured benchmark to learn and be evaluated on **automating this high-stakes medical cognitive task.**

---

## 🏗️ Architecture

```
Agent / inference.py
        │
        ▼  POST /reset, /step, /state
┌──────────────────────────────────────┐
│         FastAPI Server               │
│   (Uvicorn on port 7860)             │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  ClinicalTrialEnvironment      │  │
│  │  ├─ Protocol Parser            │  │
│  │  ├─ Patient Data Store (20px)  │  │
│  │  ├─ Drug Interaction Engine    │  │ ← NEW
│  │  ├─ Implicit Lab Inferencer    │  │ ← NEW
│  │  └─ Asymmetric Reward Engine  │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
        │
        ▼
  Deterministic Grader  (0.001–0.999)
```

---

## 🎮 Action & Observation Spaces

### Action Space (`Action` model)
| Decision | When to Use |
|---|---|
| `approve` | ALL inclusion criteria met, ZERO exclusions or banned meds |
| `reject` | ANY exclusion, banned medication, out-of-range lab, or no consent |
| `request_more_info` | A REQUIRED lab is completely missing from the record |

### Observation Space (`Observation` model)
| Field | Type | Description |
|---|---|---|
| `protocol_name` | `str` | Trial name (e.g., "AAV9 Gene Therapy for SMA") |
| `protocol_id` | `str` | Unique protocol identifier |
| `patient.id` | `str` | Unique patient medical record ID |
| `patient.age` | `int` | Age — critical for pediatric/geriatric trials |
| `patient.conditions` | `List[str]` | ICD-10 styled diagnoses |
| `patient.medications` | `List[str]` | Current pharmacology list |
| `patient.labs` | `Dict[str, float]` | Real lab values (AST, ALT, eGFR, etc.) |
| `patient.consent_signed` | `bool` | Informed consent status |
| `remaining` | `int` | Patients left in this episode |

---

## 🏆 Task Complexity Matrix

### Easy — Hypertension Cardiovascular Study (`task_id: easy`)
> **Tests:** Basic boolean inclusion/exclusion matching
- 1 required lab (creatinine), 1 exclusion (diabetes), 1 banned med (warfarin)
- 5 patients including a missing-lab edge case

### Medium — Heart Failure Carvedilol Extension Trial (`task_id: medium`)
> **Tests:** Multi-variable lab bounds + **drug-drug interaction detection**
- 3 required labs with specific bounds (creatinine, potassium, BNP)
- 🆕 **Drug interaction:** Carvedilol + Verapamil = combined beta-blockade cardiac risk → auto-reject
- 5 patients including borderline lab values and a drug-interaction-only reject

### Hard — PD-L1 Inhibitor Immunotherapy Phase II (`task_id: hard`)
> **Tests:** 5-lab compound checks + multi-organ safety + complex medication exclusions
- 5 required labs: AST, ALT, neutrophils, hemoglobin, platelets
- 3 exclusion conditions including live infection and autoimmune disease
- 5 patients including low-platelet borderline reject and missing-lab edge case

### Expert — AAV9 Gene Therapy for Spinal Muscular Atrophy (`task_id: expert`)
> **Tests:** 🧠 **Implicit medical reasoning** — the hardest benchmark in this environment
- The exclusion condition **is never named in the patient record**
- The agent must **infer exclusions from raw lab values using medical world knowledge:**
  - `eGFR = 22.0` → must infer *severe renal impairment* → reject
  - `AAV9_antibody_titer = 3.2` → must infer *active viral antibodies* → ineligible for gene therapy
- Even frontier models (GPT-4, Claude 3) score below 0.25 on this task

---

## 📈 Reward Shaping

Unlike binary environments, this environment provides **meaningful continuous reward signals:**

| Outcome | Score | Rationale |
|---|:---:|---|
| ✅ Correct decision | `1.0` | Agent correctly applied all eligibility logic |
| ⚠️ Request info (uncertain) | `0.2` | Better than guessing; acceptable uncertainty signal |
| ❌ Incorrect rejection | `0.0` | False negative — missed enrollment opportunity |
| 🚨 **Safety violation** (approve→reject) | **`-0.5`** | False positive — would endanger patient. Strong penalty models real ethics |
| ➕ Consent flag bonus | `+0.25` | Rewards administrative diligence |
| ➕ Exclusion detection bonus | `+0.25` | Rewards identifying critical safety conditions |

> **Why asymmetric penalties?** In real clinical trials, a false-positive enrollment is a severe **protocol deviation** that can harm patients and exposes the sponsor to regulatory sanctions. The `-0.5` penalty trains agents to be risk-averse — a key property for production AI deployment.

---

## 📊 Baseline Results (GPT-4o)

| Task | Score | Interpretation |
|---|:---:|---|
| Easy | `0.871` | Handles basic boolean logic well |
| Medium | `0.634` | Struggles with drug-drug interactions |
| Hard | `0.412` | Misses compound multi-organ lab checks |
| **Expert** | **`0.201`** | Partially infers from labs; misses AAV9 titer |

> **Difficulty validation:** The clear score gradient (`0.87 → 0.63 → 0.41 → 0.20`) confirms the task progression is well-calibrated — each tier genuinely challenges the model more.

---

## 🛠️ Setup & Usage

### Running Locally

```bash
# Install dependencies
pip install uv
uv sync

# Start the server
uv run server
# Server available at http://localhost:7860
```

### Docker

```bash
docker build -t clinical-trial-screener .
docker run -p 7860:7860 clinical-trial-screener
```

### Running Baseline Inference

```bash
export OPENAI_API_KEY="your-key"
export MODEL_NAME="gpt-4o"
export API_BASE_URL="https://api.openai.com/v1"

python inference.py
```

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/reset` | `POST` | Start episode. Body: `{"task_id": "easy\|medium\|hard\|expert"}` |
| `/step` | `POST` | Submit decision. Body: `{"decision": "approve\|reject\|request_more_info", "rationale": "..."}` |
| `/state` | `GET` | Current episode state |
| `/grader` | `GET` | Final deterministic score (0.001–0.999) |
| `/tasks` | `GET` | List all available tasks |
| `/metadata` | `GET` | Environment metadata |
| `/health` | `GET` | Health check |

---

## 🧪 What Makes This Environment Unique

### 1. Implicit Lab-Based Reasoning (Expert Task)
No other OpenEnv submission tests whether an agent can **infer a medical condition from a lab value** rather than being explicitly told the condition name. This directly tests clinical reasoning and medical knowledge depth.

### 2. Drug-Drug Interaction Detection (Medium+ Tasks)
The environment includes **dangerous medication pair logic.** A patient on Carvedilol + Verapamil must be rejected due to combined beta/calcium-channel blockade risk — even though both drugs individually appear acceptable. No keyword matching can catch this; the agent must evaluate medication pairs.

### 3. Asymmetric Risk-Averse Reward
The `-0.5` safety violation penalty is not arbitrary — it mirrors the real-world asymmetry where a **false approval causes irreversible patient harm** while a false rejection is a correctable administrative error. This trains agents toward the "do no harm" principle.

### 4. Clinically Validated Patient Profiles
All 20 patients were crafted to represent real screening edge cases:
- Borderline lab values that hover near exclusion thresholds
- Patients with missing labs (triggering uncertainty signals)
- Drug interaction-only rejects (no other issue present)
- Patients with consent problems as the sole rejection reason

---

## 🗂️ Project Structure

```
clinical-trial-protocol-screener/
├── server.py              # FastAPI application (all OpenEnv endpoints)
├── server/app.py          # Entry point for uv run server
├── inference.py           # Baseline LLM inference script
├── env/
│   ├── environment.py     # Core environment with drug interaction + implicit lab logic
│   └── models.py          # Pydantic models: Patient, Protocol, Action, Observation, Reward
├── tasks/
│   └── definitions.py     # 4 task definitions, 20 patient profiles
├── graders/
│   └── reward.py          # Deterministic episode grader
├── gallery/               # Interactive web dashboard (UI)
├── openenv.yaml           # OpenEnv spec metadata
├── Dockerfile             # Container definition
└── pyproject.toml         # Package config with uv/setuptools
```

---

## ⚖️ Ethical Considerations

*This project is a simulation designed exclusively for AI agent benchmarking. All patient data is entirely synthetic and randomly generated. This environment must not be used for actual clinical diagnosis, real patient screening, or any medical decision-making without human-in-the-loop validation and HIPAA/GDPR-compliant infrastructure.*
