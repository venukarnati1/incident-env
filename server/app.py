"""
Project: Incident Resolution Environment
Built by: Vebnox
"""
import sys
import os
import uvicorn
from fastapi import FastAPI, Request

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.environment import IncidentEnv
from env.models import Action
from env.grader import grade_easy_task, grade_medium_task, grade_hard_task

app = FastAPI(title="Incident Resolution Environment — Built by Vebnox")

# Global env state per session (single-agent, stateful)
_env: IncidentEnv = None
_task_id: str = "easy"

# Task registry — used by /tasks and /grade endpoints for validator discovery
TASK_REGISTRY = {
    "easy": {
        "id": "easy",
        "description": "Classify customer issue correctly in 1-2 steps",
        "difficulty": "easy",
        "grader": "env.grader:grade_easy_task",
        "has_grader": True,
        "grader_fn": grade_easy_task,
    },
    "medium": {
        "id": "medium",
        "description": "Classify and respond to customer issue in 2-3 steps",
        "difficulty": "medium",
        "grader": "env.grader:grade_medium_task",
        "has_grader": True,
        "grader_fn": grade_medium_task,
    },
    "hard": {
        "id": "hard",
        "description": "Handle angry premium customer: classify, escalate, assign team in 4-5 steps",
        "difficulty": "hard",
        "grader": "env.grader:grade_hard_task",
        "has_grader": True,
        "grader_fn": grade_hard_task,
    },
}


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Incident Resolution Environment is running.",
        "built_by": "Vebnox — AI & Automation Solutions",
        "endpoints": ["/tasks", "/run/{task}", "/reset", "/step", "/state", "/grade/{task_id}"],
        "tasks": list(TASK_REGISTRY.keys()),
    }


@app.get("/tasks")
def list_tasks():
    """Return all available tasks and their grader metadata — required by OpenEnv validator."""
    tasks = []
    for task_id, meta in TASK_REGISTRY.items():
        tasks.append({
            "id": meta["id"],
            "description": meta["description"],
            "difficulty": meta["difficulty"],
            "grader": meta["grader"],
            "has_grader": meta["has_grader"],
        })
    return {"tasks": tasks, "count": len(tasks)}


@app.post("/grade/{task_id}")
async def grade_task(task_id: str, request: Request):
    """
    Grade a completed task trajectory.
    Accepts: {"state": {...}, "score": 0.85, "action_history": [...]}
    Returns: {"score": float, "success": bool, "task_id": str}
    """
    if task_id not in TASK_REGISTRY:
        return {"score": 0.0, "success": False, "error": f"Unknown task: {task_id}"}

    try:
        body = await request.json()
    except Exception:
        body = {}

    state = body.get("state", {}) if isinstance(body, dict) else {}
    raw_score = float(body.get("score", 0.0)) if isinstance(body, dict) else 0.0
    action_history = body.get("action_history", []) if isinstance(body, dict) else []

    # Merge action_history into state for grader compatibility
    state["action_history"] = action_history
    if "crm_status" not in state:
        state["crm_status"] = "Open"

    grader_fn = TASK_REGISTRY[task_id]["grader_fn"]
    final_score = grader_fn(state, raw_score)
    final_score = round(min(1.0, max(0.0, final_score)), 4)

    return {
        "task_id": task_id,
        "score": final_score,
        "success": final_score >= 0.1,
        "grader": TASK_REGISTRY[task_id]["grader"],
    }


@app.get("/run/{task}")
def run_task(task: str):
    """Reset and return initial state for a given task difficulty."""
    global _env, _task_id
    if task not in TASK_REGISTRY:
        task = "easy"
    _task_id = task
    _env = IncidentEnv()

    if task == "easy":
        state = _env.reset(issue_type=None, user_mood="neutral", customer_tier="free")
    elif task == "medium":
        state = _env.reset(issue_type=None, user_mood=None, customer_tier="premium")
        _env.obs.missing_info = False
        state["missing_info"] = False
    else:
        state = _env.reset(issue_type=None, user_mood="angry", customer_tier="premium")

    return {"env": {
        "obs": state,
        "step_count": _env.step_count,
        "current_reward": _env.current_reward,
        "is_done": _env.is_done,
        "expected_issue": _env.expected_issue,
        "action_history": _env.action_history
    }, "state": state}


@app.post("/reset")
async def reset_env(request: Request):
    """Reset environment to initial state."""
    global _env, _task_id
    try:
        body = await request.json()
    except Exception:
        body = {}

    task = body.get("task", "easy") if isinstance(body, dict) else "easy"
    if task not in TASK_REGISTRY:
        task = "easy"
    _task_id = task
    _env = IncidentEnv()

    if task == "easy":
        state = _env.reset(issue_type=None, user_mood="neutral", customer_tier="free")
    elif task == "medium":
        state = _env.reset(issue_type=None, user_mood=None, customer_tier="premium")
        _env.obs.missing_info = False
        state["missing_info"] = False
    else:
        state = _env.reset(issue_type=None, user_mood="angry", customer_tier="premium")

    return {"state": state, "reward": 0.0, "done": False, "info": {"task": task}}


@app.post("/step")
async def step_env(request: Request):
    """Execute one action step in the environment."""
    global _env, _task_id
    if _env is None:
        return {"state": {}, "reward": 0.0, "done": True, "info": {"error": "Environment not initialized. Call /reset first."}}

    try:
        body = await request.json()
    except Exception:
        body = {}

    action_type = body.get("action", "ignore") if isinstance(body, dict) else "ignore"
    payload = body.get("payload", None) if isinstance(body, dict) else None

    allowed = ["classify_issue", "decide_action", "reply_user", "escalate_issue", "assign_team", "request_more_info", "ignore"]
    if action_type not in allowed:
        action_type = "ignore"

    action = Action(action_type=action_type, payload=payload)
    state, reward, done, info = _env.step(action)

    return {"state": state, "reward": reward, "done": done, "info": info}


@app.get("/state")
def get_state():
    """Return current environment state."""
    global _env
    if _env is None:
        return {}
    return _env.state()


def main():
    """Entry point for 'server' console script and multi-mode deployment."""
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()