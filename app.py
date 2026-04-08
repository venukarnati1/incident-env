from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/reset")
def reset():
    return {"status": "reset"}

@app.post("/step")
def step(action: dict):
    task = action.get("task", "easy")

    result = subprocess.run(
        ["python", "inference.py", "--task", task],
        capture_output=True,
        text=True
    )

    return {"result": result.stdout}
