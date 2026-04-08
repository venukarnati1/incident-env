"""
Project: Incident Resolution Environment
Built by: Vebnox (vebnox.com)
"""
from pydantic import BaseModel
from typing import Literal, Optional, List

class Observation(BaseModel):
    issue_type: Literal['payment failed', 'order not delivered', 'app crash', 'refund request']
    user_mood: Literal['angry', 'neutral', 'happy']
    customer_tier: Literal['free', 'premium']
    crm_status: str
    missing_info: bool
    conversation_history: List[str]
    past_actions: List[str]

class Action(BaseModel):
    action_type: Literal['classify_issue', 'decide_action', 'reply_user', 'escalate_issue', 'assign_team', 'request_more_info', 'ignore']
    payload: Optional[str] = None

class Reward(BaseModel):
    score: float
