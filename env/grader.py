"""
Project: Incident Resolution Environment
Built by: Vebnox (vebnox.com)
"""
def grade_easy_task(env_state, final_score: float) -> float:
    if env_state.get('crm_status') == 'Failed_Sequence':
        return 0.0
    actions = env_state.get('action_history', [])
    if 'classify_issue' in actions:
        return min(1.0, max(0.0, final_score))
    return 0.0

def grade_medium_task(env_state, final_score: float) -> float:
    actions = env_state.get('action_history', [])
    if 'classify_issue' in actions and 'reply_user' in actions:
        return min(1.0, max(0.0, final_score))
    return max(0.0, final_score - 0.5)

def grade_hard_task(env_state, final_score: float) -> float:
    actions = env_state.get('action_history', [])
    if 'escalate_issue' in actions and 'assign_team' in actions:
        return min(1.0, max(0.0, final_score))
    return 0.0
