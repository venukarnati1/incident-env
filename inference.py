"""
Project: Incident Resolution Environment
Built by: Vebnox (vebnox.com)
"""
# This environment simulates LLM behavior using deterministic logic for reproducibility
import os
import argparse
import json
from env.models import Action
from env.tasks import run_easy_task, run_medium_task, run_hard_task
from env.grader import grade_easy_task, grade_medium_task, grade_hard_task

API_BASE_URL = os.getenv("API_BASE_URL", "local-env")
MODEL_NAME = os.getenv("MODEL_NAME", "default-agent")
HF_TOKEN = os.getenv("HF_TOKEN")

# Simulated LLM behavior using deterministic policy

def run_inference(task_id: str):
    print(f"[START] task={task_id} env=incident-env model=default-agent")
    
    if task_id == 'easy':
        env, state = run_easy_task()
        steps_actions = []
        if state['missing_info']: steps_actions.append(Action(action_type='request_more_info'))
        steps_actions.append(Action(action_type='classify_issue', payload=state['issue_type']))
        grader_func = grade_easy_task
    elif task_id == 'medium':
        env, state = run_medium_task()
        steps_actions = []
        if state['missing_info']: steps_actions.append(Action(action_type='request_more_info'))
        steps_actions.extend([
            Action(action_type='classify_issue', payload=state['issue_type']),
            Action(action_type='decide_action', payload='prepare_reply'),
            Action(action_type='reply_user', payload='Let me process this refund.'),
        ])
        grader_func = grade_medium_task
    elif task_id == 'hard':
        env, state = run_hard_task()
        steps_actions = []
        if state['missing_info']: steps_actions.append(Action(action_type='request_more_info'))
        steps_actions.extend([
            Action(action_type='classify_issue', payload=state['issue_type']),
            Action(action_type='decide_action', payload='prepare_escalation'),
            Action(action_type='escalate_issue'),
            Action(action_type='assign_team'),
        ])
        grader_func = grade_hard_task
    else:
        print("[END] success=false steps=0 score=0.00 rewards=")
        return

    total_rewards = []
    done = False
    step_num = 0
    
    for action in steps_actions:
        step_num += 1
        state, reward, done, info = env.step(action)
        total_rewards.append(reward)
        
        err_str = "null" if not info.get("error") else info["error"]
        print(f"[STEP] step={step_num} action={action.action_type} reward={reward:.2f} done={str(done).lower()} error={err_str}")
        if done:
            break
            
    raw_score = sum(total_rewards)
    state['action_history'] = env.action_history
    
    # Store dynamic variables to properly execute failure tracking
    state['crm_status'] = env.obs.crm_status
    
    final_score = grader_func(state, raw_score)
    final_score = min(1.0, max(0.0, final_score))
    
    if state['crm_status'] == 'Failed_Sequence':
        final_score = 0.0
        success_str = "false"
    elif not done and task_id != 'easy':
        final_score = min(final_score, 0.49)
        success_str = "false"
    else:
        if task_id == 'easy':
            success_str = "true" if final_score > 0.0 else "false"
        else:
            success_str = "true" if final_score >= 0.5 else "false"
    
    r_str = ",".join([f"{r:.2f}" for r in total_rewards])
    
    print(f"[END] success={success_str} steps={step_num} score={final_score:.2f} rewards={r_str}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, required=True, choices=['easy', 'medium', 'hard'])
    args = parser.parse_args()
    run_inference(args.task)
