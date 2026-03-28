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
    tasks = ["easy", "medium", "hard"]
    final_results = {}

    print(f"Starting Baseline Inference using model: {MODEL_NAME}")
    print("-" * 50)

    for task_id in tasks:
        print(f"Running Task: {task_id}...")
        obs = env.reset(task_id)
        done = False
        
        while not done:
            # Construct a prompt for the medical screening task
            prompt = f"""
            You are a Clinical Trial Screening Assistant. 
            Decision Task for Protocol: {obs.protocol_name}
            
            PATIENT DATA:
            - ID: {obs.patient.id}
            - Age: {obs.patient.age}
            - Sex: {obs.patient.sex}
            - Conditions: {', '.join(obs.patient.conditions)}
            - Medications: {', '.join(obs.patient.medications)}
            - Lab Results: {json.dumps(obs.patient.labs)}
            - Consent Signed: {obs.patient.consent_signed}
            
            YOUR OBJECTIVE:
            Decide if this patient should be 'approve' (matches all criteria), 'reject' (fails criteria), 
            or if you need 'request_more_info' (missing critical labs).
            
            Return your decision in the following JSON format:
            {{
                "decision": "approve" | "reject" | "request_more_info",
                "rationale": "Brief explanation of your decision"
            }}
            """

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
                
                print(f"  Decision for {obs.patient.id}: {action.decision.upper()}")
                obs, reward, done, _ = env.step(action)
                
            except Exception as e:
                print(f"  Error during inference: {e}")
                break

        # Get final score from the grader
        from graders.reward import grade_episode
        result = grade_episode(env)
        final_results[task_id] = result
        print(f"  Final Score for {task_id}: {result['score']}")
        print("-" * 50)

    print("\n--- BASELINE REPRODUCIBILITY SUMMARY ---")
    print(json.dumps(final_results, indent=2))
    
    # Write to a file for README inclusion
    with open("baseline_results.json", "w") as f:
        json.dump(final_results, f, indent=2)

if __name__ == "__main__":
    run_inference()
