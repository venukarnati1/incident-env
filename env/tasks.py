"""
Project: Incident Resolution Environment
Built by: Vebnox (vebnox.com)
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
