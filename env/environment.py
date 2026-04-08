"""
Project: Incident Resolution Environment
Built by: Vebnox (vebnox.com)
"""
import random
from env.models import Observation, Action
from typing import Tuple, Dict, Any, Union

class IncidentEnv:
    def __init__(self):
        self.obs = None
        self.step_count = 0
        self.current_reward = 0.0
        self.is_done = False
        self.expected_issue = None
        self.action_history = []

    def reset(self, issue_type: str = None, user_mood: str = None, customer_tier: str = None) -> Dict[str, Any]:
        issues = ['payment failed', 'order not delivered', 'app crash', 'refund request']
        moods = ['angry', 'neutral', 'happy']
        tiers = ['free', 'premium']
        
        self.expected_issue = issue_type if issue_type else random.choice(issues)
        mood = user_mood if user_mood else random.choice(moods)
        tier = customer_tier if customer_tier else random.choice(tiers)
        
        self.obs = Observation(
            issue_type=self.expected_issue,
            user_mood=mood,
            customer_tier=tier,
            crm_status="Open",
            missing_info=random.choice([True, False]),
            conversation_history=[f"User [{mood}]: I have an issue regarding {self.expected_issue}."],
            past_actions=[]
        )
        self.step_count = 0
        self.current_reward = 0.0
        self.is_done = False
        self.action_history = []
        return self.state()

    def step(self, action_input: Union[Dict[str, Any], Action]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        if isinstance(action_input, dict):
            action = Action(**action_input)
        else:
            action = action_input

        if self.is_done or self.step_count >= 10:
            return self.state(), 0.0, True, {"error": "Episode already done."}

        self.step_count += 1
        self.action_history.append(action.action_type)
        step_reward = -0.05 # Baseline optimality penalty to encourage fast resolution
        error = None

        self.obs.past_actions.append(action.action_type)

        # 1. Unnecessary actions penalty
        if len(self.obs.past_actions) > 1 and self.obs.past_actions[-1] == self.obs.past_actions[-2]:
            step_reward -= 0.2
            error = "Penalty: Unnecessary repeated step."
            
        # 2. Sequence checks
        if action.action_type == 'decide_action' and 'classify_issue' not in self.obs.past_actions[:-1]:
            step_reward -= 0.5
            error = "Penalty: wrong sequence! Must classify_issue before decide_action."
            self.obs.user_mood = 'angry'
            self.obs.crm_status = "Failed_Sequence"
            
        elif action.action_type in ['reply_user', 'escalate_issue', 'assign_team'] and 'decide_action' not in self.obs.past_actions[:-1]:
            # For easy tasks, they might not need this if they only do classify_issue. But if they take these actions, they must decide first.
            step_reward -= 0.5
            error = "Penalty: wrong sequence! Must decide_action before executing resolution."
            self.obs.user_mood = 'angry'
            self.obs.crm_status = "Failed_Sequence"

        if self.obs.missing_info and action.action_type not in ['request_more_info', 'ignore']:
            step_reward -= 0.3
            error = "Penalty: Cannot proceed while missing critical info!"
            self.obs.user_mood = 'angry'
            
        elif action.action_type == 'classify_issue':
            if action.payload == self.expected_issue:
                step_reward += 0.2 # partial reward
                if self.obs.customer_tier == 'free' and self.obs.user_mood == 'neutral':
                    self.is_done = True # Easy task completion boundary
            elif action.payload and len(action.payload) > 3:
                # slightly incorrect classification
                step_reward -= 0.1 
                error = "Classification slightly incorrect"
            else:
                step_reward -= 0.3 # wrong classification
                error = "Incorrect classification"
                
        elif action.action_type == 'decide_action':
            if 'classify_issue' in self.obs.past_actions[:-1]:
                step_reward += 0.1 # partial reward
            
        elif action.action_type == 'reply_user':
            if action.payload and len(action.payload.strip()) > 0:
                self.obs.conversation_history.append(f"Agent: {action.payload}")
                step_reward += 0.1 # partial reward
                step_reward += 0.1 # good response tone
                if self.obs.user_mood == 'angry':
                    self.obs.user_mood = 'neutral'
                step_reward += 0.5 # final resolution reward
                self.is_done = True
            else:
                step_reward -= 0.3
                error = "Empty reply_user payload"
                
        elif action.action_type == 'escalate_issue':
            step_reward += 0.1 # partial reward
            self.obs.crm_status = "Escalated"
            
        elif action.action_type == 'assign_team':
            if 'escalate_issue' in self.obs.past_actions[:-1]:
                step_reward += 0.1 # partial reward
            self.obs.crm_status = "Assigned"
            self.is_done = True
            step_reward += 0.5 # final resolution reward
            if self.obs.user_mood != 'happy':
                self.obs.user_mood = 'happy'
                
        elif action.action_type == 'request_more_info':
            if self.obs.missing_info:
                step_reward += 0.1
                self.obs.conversation_history.append("Agent: Can you provide more info?")
                self.obs.missing_info = False
                self.obs.conversation_history.append("User: Here is the missing tracking number.")
            else:
                step_reward -= 0.05
                error = "Penalty: Information was not missing!"
                self.obs.conversation_history.append("Agent: Can you provide more info?")
                self.obs.conversation_history.append("User: I already gave you all the information!")
            
        elif action.action_type == 'ignore':
            step_reward -= 0.5
            self.obs.crm_status = "Closed_Unresolved"
            self.is_done = True
            
        if self.step_count >= 10:
            self.is_done = True

        # Mood variability applied dynamically on resolution
        if self.is_done:
            if self.obs.user_mood == 'happy':
                step_reward += 0.1
            elif self.obs.user_mood == 'angry':
                step_reward -= 0.1

        # Total normalization ensures total sum is clamped [0, 1] without mutating raw sum externally
        new_total = max(0.0, min(1.0, self.current_reward + step_reward))
        final_step_reward = new_total - self.current_reward
        self.current_reward = new_total

        info = {"error": error, "action_taken": action.action_type}
        
        return self.state(), round(final_step_reward, 2), self.is_done, info

    def state(self) -> Dict[str, Any]:
        return self.obs.model_dump()
