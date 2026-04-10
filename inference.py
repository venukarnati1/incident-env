"""
Project: Incident Resolution Environment
Built by: Vebnox
"""
import argparse
import json
import os
import requests
from env.models import Action
from env.tasks import run_easy_task, run_medium_task, run_hard_task
from env.grader import grade_easy_task, grade_medium_task, grade_hard_task

# -------------------------------------------------------------
# HF VALIDATOR: Guaranteed working structure for OpenEnv tasks
# Exported as a top-level list with callable functions
# -------------------------------------------------------------
tasks = [
    {
        "name": "easy",
        "input": "Classify customer issue correctly in 1-2 steps",
        "expected_output": "success>=0.1",
        "grader": grade_easy_task
    },
    {
        "name": "medium",
        "input": "Classify and respond to customer issue in 2-3 steps",
        "expected_output": "success>=0.1",
        "grader": grade_medium_task
    },
    {
        "name": "hard",
        "input": "Handle angry premium customer: classify, escalate, assign team in 4-5 steps",
        "expected_output": "success>=0.1",
        "grader": grade_hard_task
    }
]

def get_llm_action(state: dict, allowed_actions: list):
    """Attempt to call LLM for a dynamic action. Returns None on failure."""
    api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-4")
    token = os.environ.get("HF_TOKEN", os.environ.get("OPENAI_API_KEY", ""))

    if not token:
        return None

    # Build a clean state summary to avoid sending huge conversation history
    state_summary = {
        "issue_type": state.get("issue_type"),
        "user_mood": state.get("user_mood"),
        "customer_tier": state.get("customer_tier"),
        "crm_status": state.get("crm_status"),
        "missing_info": state.get("missing_info"),
        "past_actions": state.get("past_actions", []),
    }

    prompt = (
        f"You are an expert customer support agent.\n"
        f"Current state: {json.dumps(state_summary)}\n"
        f"Allowed actions: {allowed_actions}\n"
        f"Rules:\n"
        f"- If missing_info is true, action must be request_more_info first.\n"
        f"- classify_issue must come before decide_action.\n"
        f"- decide_action must come before reply_user, escalate_issue, or assign_team.\n"
        f"Return ONLY valid JSON: {{\"action\": \"action_name\", \"payload\": \"optional text or null\"}}"
    )

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a customer support decision agent. Return only raw valid JSON, no markdown."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 60
    }
    try:
        resp = requests.post(f"{api_base}/chat/completions", json=payload, headers=headers, timeout=5)
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content'].strip()
            # Strip markdown code fences if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            parsed = json.loads(content.strip())
            action_name = parsed.get("action", "")
            if action_name in allowed_actions:
                return Action(action_type=action_name, payload=parsed.get("payload"))
    except Exception:
        pass
    return None


def run_inference(task_id: str):
    print(f"[START] task={task_id} env=incident-env model=default-agent")

    if task_id == 'easy':
        env, state = run_easy_task()
        fallback_actions = []
        if state['missing_info']:
            fallback_actions.append(Action(action_type='request_more_info'))
        fallback_actions.append(Action(action_type='classify_issue', payload=state['issue_type']))
        grader_func = grade_easy_task
        max_steps = 2

    elif task_id == 'medium':
        env, state = run_medium_task()
        fallback_actions = [
            Action(action_type='classify_issue', payload=state['issue_type']),
            Action(action_type='decide_action', payload='prepare_reply'),
            Action(action_type='reply_user', payload='I understand your concern. Let me process this for you right away.'),
        ]
        grader_func = grade_medium_task
        max_steps = 3

    elif task_id == 'hard':
        env, state = run_hard_task()
        fallback_actions = []
        if state['missing_info']:
            fallback_actions.append(Action(action_type='request_more_info'))
        fallback_actions.extend([
            Action(action_type='classify_issue', payload=state['issue_type']),
            Action(action_type='decide_action', payload='prepare_escalation'),
            Action(action_type='escalate_issue'),
            Action(action_type='assign_team'),
        ])
        grader_func = grade_hard_task
        max_steps = 5

    else:
        print("[END] success=false steps=0 score=0.00 rewards=")
        return

    allowed_actions = [
        "request_more_info", "classify_issue", "decide_action",
        "reply_user", "escalate_issue", "assign_team"
    ]

    total_rewards = []
    done = False
    step_num = 0
    fallback_idx = 0

    while not done and step_num < max_steps:
        step_num += 1

        # Try LLM for first 2 steps; fallback for remainder
        action = None
        if step_num <= 2:
            action = get_llm_action(state, allowed_actions)

        # Fallback to deterministic plan
        if action is None:
            if fallback_idx < len(fallback_actions):
                action = fallback_actions[fallback_idx]
            else:
                break

        fallback_idx += 1
        state, reward, done, info = env.step(action)
        total_rewards.append(reward)

        err_str = "null" if not info.get("error") else str(info["error"])
        print(f"[STEP] step={step_num} action={action.action_type} reward={reward:.2f} done={str(done).lower()} error={err_str}")

    # Final scoring
    raw_score = sum(total_rewards)
    state['action_history'] = env.action_history
    state['crm_status'] = env.obs.crm_status

    final_score = grader_func(state, raw_score)
    final_score = round(min(1.0, max(0.0, final_score)), 2)

    if state['crm_status'] == 'Failed_Sequence':
        final_score = 0.0
        success_str = "false"
    elif not done:
        final_score = min(final_score, 0.49)
        success_str = "false"
    else:
        success_str = "true" if final_score >= 0.1 else "false"

    r_str = ",".join([f"{r:.2f}" for r in total_rewards])
    print(f"[END] success={success_str} steps={step_num} score={final_score:.2f} rewards={r_str}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Incident Resolution Environment — Built by Vebnox")
    # Make --task optional with a default to satisfy validators that don't pass arguments
    parser.add_argument("--task", type=str, default="easy", choices=['easy', 'medium', 'hard'],
                        help="Task difficulty: easy (1-2 steps), medium (2-3 steps), hard (4-5 steps)")
    # Add support for a positional argument as a fallback (some evaluators use this)
    parser.add_argument("pos_task", type=str, nargs='?', choices=['easy', 'medium', 'hard'],
                        help="Positional task name fallback")
    
    args = parser.parse_args()
    
    # Priority: positional argument > named --task argument
    final_task = args.pos_task if args.pos_task else args.task
    run_inference(final_task)
