import os
import json
import argparse
from openai import OpenAI
from env.environment import ClinicalTrialEnvironment
from env.models import Action

# Round 1 Requirement: Use these environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")

def run_inference():
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY or HF_TOKEN environment variable not set.")
        return

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=API_BASE_URL
    )

    env = ClinicalTrialEnvironment()
    tasks = ["easy", "medium", "hard", "expert"]
    final_results = {}

    print(f"Starting Baseline Inference | model={MODEL_NAME}", flush=True)

    for task_id in tasks:
        print(f"[START] task={task_id}", flush=True)
        # obs = env.reset(task_id)
        obs = env.reset(task_id)
        done = False
        steps = 0
        
        while not done:
            protocol = env.protocol
            prompt = f"""You are a senior Clinical Research Coordinator (CRC) screening patients for a clinical trial.

TRIAL: {obs.protocol_name} (ID: {obs.protocol_id})
INCLUSION CRITERIA: {', '.join(protocol.inclusion)}
EXCLUSION CRITERIA: {', '.join(protocol.exclusion)}
REQUIRED LABS (with acceptable ranges): {json.dumps(protocol.required_labs)}
BANNED MEDICATIONS: {', '.join(protocol.banned_medications)}

PATIENT RECORD:
- Patient ID: {obs.patient.id}
- Age: {obs.patient.age} | Sex: {obs.patient.sex}
- Conditions: {', '.join(obs.patient.conditions) or 'None reported'}
- Current Medications: {', '.join(obs.patient.medications) or 'None'}
- Lab Results: {json.dumps(obs.patient.labs) or 'None available'}
- Informed Consent Signed: {obs.patient.consent_signed}

TASK: Screen this patient against all trial criteria above.
- Choose 'approve' ONLY if ALL inclusion criteria are met AND NO exclusion criteria or banned medications are present AND all required labs are within range.
- Choose 'reject' if ANY exclusion criterion is met, OR a banned medication is present, OR a lab value is out of range, OR consent is not signed.
- Choose 'request_more_info' ONLY if a required lab value is completely missing from the record.
- IMPORTANT: If a lab value implies a condition (e.g., very low eGFR implies renal impairment), treat that as an exclusion even if not explicitly labeled.

Respond with valid JSON only:
{{
    "decision": "approve" | "reject" | "request_more_info",
    "rationale": "Concise clinical reasoning for your decision"
}}"""


            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                res_data = json.loads(response.choices[0].message.content)
                action = Action(
                    decision=res_data.get("decision", "reject"),
                    rationale=res_data.get("rationale", "")
                )
                
                obs, reward, done, _ = env.step(action)
                steps += 1
                
                reward_val = getattr(reward, "value", float(reward)) if hasattr(reward, "value") else float(reward)
                print(f"[STEP] step={steps} reward={reward_val}", flush=True)
                
            except Exception as e:
                # Silently fail for parser stability, just break loop
                break

        # Get final score from the grader
        from graders.reward import grade_episode
        result = grade_episode(env)
        final_results[task_id] = result
        print(f"[END] task={task_id} score={result['score']} steps={steps}", flush=True)

    print("\n--- BASELINE REPRODUCIBILITY SUMMARY ---")
    print(json.dumps(final_results, indent=2))
    
    # Write to a file for README inclusion
    with open("baseline_results.json", "w") as f:
        json.dump(final_results, f, indent=2)

if __name__ == "__main__":
    run_inference()
