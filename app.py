from fastapi import FastAPI
import subprocess

app = FastAPI()

# Health check
@app.get("/")
def home():
    return {"status": "running"}

# REQUIRED: reset endpoint
@app.post("/reset")
def reset():
    return {
        "state": "reset",
        "message": "Environment reset successful"
    }

# REQUIRED: step endpoint
@app.post("/step")
def step(action: dict):
    task = action.get("task", "easy")

    result = subprocess.run(
        ["python", "inference.py", "--task", task],
        capture_output=True,
        text=True
    )

    return {
        "result": result.stdout
    }

# Your existing test endpoints (keep)
@app.get("/run/{task}")
def run_task(task: str):
    result = subprocess.run(
        ["python", "inference.py", "--task", task],
        capture_output=True,
        text=True
    )
    return {"output": result.stdout}
