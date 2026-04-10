---
title: Incident Env
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

---

# 🏢 Incident Resolution Environment

> **Built by Vebnox — AI & Automation Solutions**

A production-grade **OpenEnv-compliant** AI training environment that simulates real-world customer incident resolution workflows. AI agents must **classify, prioritize, and resolve** support tickets through structured multi-step decision-making — with penalties for wrong sequences and inefficient actions.

The environment enforces sequential decision-making and penalizes inefficient workflows, ensuring agents learn optimal task execution strategies under realistic constraints.

---

## 📌 Features

- ✅ **OpenEnv Compliant** — `step()`, `reset()`, `state()` with full Pydantic typed models
- ✅ **3 Task Difficulties** — Easy (1-2 steps), Medium (2-3 steps), Hard (4-5 steps)
- ✅ **Stateful Memory** — Tracks `conversation_history`, `past_actions`, `crm_status`
- ✅ **Sequence Enforcement** — Wrong action order is penalized (`-0.5` reward penalty)
- ✅ **User Mood & Tier** — `angry/neutral/happy` × `free/premium` affect rewards dynamically
- ✅ **LLM Decision Layer** — Plugs into OpenAI / HuggingFace inference endpoints
- ✅ **Deterministic Fallback** — Works without any API token (zero crashes)
- ✅ **FastAPI Server** — Live REST API at `/reset`, `/step`, `/state`, `/run/{task}`

---

## 🚀 How to Use Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Inference (CLI)
Evaluate an agent trajectory for a given task difficulty:

```bash
python inference.py --task easy
python inference.py --task medium
python inference.py --task hard
```

**With LLM enabled** (optional — falls back gracefully without):
```bash
# Windows
set HF_TOKEN=your_token_here
python inference.py --task hard

# Linux/Mac
export HF_TOKEN=your_token_here
python inference.py --task hard
```

### 3. Output Format
```text
[START] task=hard env=incident-env model=default-agent
[STEP] step=1 action=request_more_info reward=0.05 done=false error=null
[STEP] step=2 action=classify_issue reward=0.15 done=false error=null
[STEP] step=3 action=decide_action reward=0.05 done=false error=null
[STEP] step=4 action=escalate_issue reward=0.05 done=false error=null
[STEP] step=5 action=assign_team reward=0.65 done=true error=null
[END] success=true steps=5 score=0.95 rewards=0.05,0.15,0.05,0.05,0.65
```

---

## 🌐 REST API (FastAPI Server)

### Run locally:
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/run/{task}` | Initialize task (`easy`, `medium`, `hard`) |
| `POST` | `/reset` | Reset environment `{"task": "hard"}` |
| `POST` | `/step` | Take action `{"action": "classify_issue", "payload": "payment failed"}` |
| `GET` | `/state` | Get current environment state |

### Example:
```bash
curl https://venukarnati-incedent-env-pro.hf.space/run/easy
curl -X POST https://venukarnati-incedent-env-pro.hf.space/step \
     -H "Content-Type: application/json" \
     -d '{"action": "classify_issue", "payload": "payment failed"}'
```

---

## 🐳 Docker

```bash
docker build -t incident-env .
docker run -p 7860:7860 -e HF_TOKEN=your_token incident-env
```

---

## 📂 Project Structure

```
incident-env/
 ├── env/
 │    ├── environment.py   # Core IncidentEnv logic
 │    ├── models.py        # Pydantic Observation, Action, Reward
 │    ├── tasks.py         # easy / medium / hard task setup
 │    ├── grader.py        # Deterministic scoring per task
 ├── server/
 │    └── app.py           # FastAPI REST server
 ├── inference.py          # CLI evaluation runner
 ├── openenv.yaml          # OpenEnv spec configuration
 ├── Dockerfile            # Docker deployment
 ├── requirements.txt
 ├── LICENSE
 └── README.md
```

---

## 🎯 Action Space

| Action | Description |
|--------|-------------|
| `request_more_info` | Ask user for missing details |
| `classify_issue` | Identify the issue type |
| `decide_action` | Choose resolution strategy |
| `reply_user` | Send resolution message to user |
| `escalate_issue` | Escalate to senior support |
| `assign_team` | Assign specialist team |
| `ignore` | Ignore issue (penalized) |

---

## 📊 Reward System

| Condition | Reward |
|-----------|--------|
| Correct classification | `+0.20` |
| Good decision | `+0.10` |
| Final resolution | `+0.50` |
| Happy user at end | `+0.10` bonus |
| Wrong action sequence | `-0.50` |
| Missing info not handled | `-0.30` |
| Unnecessary repeated step | `-0.20` |
| Ignoring the user | `-0.50` |

---

## 🌩️ Deploy to Hugging Face Spaces

```bash
huggingface-cli login
git init
git remote add origin https://huggingface.co/spaces/venukarnati/incedent-env-pro
git add .
git commit -m "Deploy Incident Env"
git push origin main
```

> Set your `HF_TOKEN` in the Space **Secrets** tab for live LLM inference.

---
