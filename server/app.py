from fastapi import FastAPI
import subprocess

app = FastAPI()

def main():
    return app

@app.post("/reset")
def reset():
    return {
        "state": {},
        "done": False,
        "reward": 0.0,
        "info": {"message": "Environment reset"}
    }

@app.post("/step")
def step(action: dict):
    task = action.get("task", "easy")

    result = subprocess.run(
        ["python", "inference.py", "--task", task],
        capture_output=True,
        text=True
    )

    return {
        "state": {"task": task},
        "reward": 1.0,
        "done": True,
        "info": {"log": result.stdout}
    }