"""
Project: Incident Resolution Environment
Built by: Vebnox
"""
from env.environment import IncidentEnv
from typing import Tuple, Dict, Any

def run_easy_task() -> Tuple[IncidentEnv, Dict[str, Any]]:
    env = IncidentEnv()
    state = env.reset(issue_type=None, user_mood='neutral', customer_tier='free')
    return env, state

def run_medium_task() -> Tuple[IncidentEnv, Dict[str, Any]]:
    env = IncidentEnv()
    state = env.reset(issue_type=None, user_mood=None, customer_tier='premium')
    # Force missing_info false to ensure step length does not exceed 3 steps (classify -> decide -> reply)
    env.obs.missing_info = False
    state['missing_info'] = False
    return env, state

def run_hard_task() -> Tuple[IncidentEnv, Dict[str, Any]]:
    env = IncidentEnv()
    state = env.reset(issue_type=None, user_mood='angry', customer_tier='premium')
    return env, state

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
