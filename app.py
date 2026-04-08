[project]
name = "incident-env"
version = "0.1.0"
description = "Autonomous Incident & Customer Issue Resolution Environment"
authors = [
    { name="Venu", email="you@example.com" }
]
dependencies = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "openenv-core>=0.2.0"
]

[project.scripts]
server = "app:app"

[tool.openenv]
entry_point = "app:app"
