from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Incident Environment Running"}

@app.get("/run/{task}")
def run_task(task: str):
    result = subprocess.run(
        ["python", "inference.py", "--task", task],
        capture_output=True,
        text=True
    )
    return {"output": result.stdout}