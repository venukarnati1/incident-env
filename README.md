---
title: Incident Resolution Environment
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_file: server/app.py
pinned: false
---

# 🚀 Autonomous Incident & Customer Issue Resolution Environment

A real-world AI environment that simulates how customer support teams handle incidents using multi-step reasoning and reward-based evaluation.

---

## 🧠 Problem

Modern businesses handle large volumes of customer issues daily:

- Issue classification  
- Decision making  
- Escalation  
- Resolution  

Training AI agents for this workflow requires structured, testable environments.

---

## 💡 Solution

This project provides an **OpenEnv-compatible environment** that simulates:

- Customer issue handling  
- Decision workflows  
- Escalation processes  
- Final resolution  

All evaluated using a **reward-based system (0–1 normalized)**.

---

## ⚙️ Features

- ✅ Multi-step reasoning (Easy / Medium / Hard)
- ✅ Deterministic environment (stable & reproducible)
- ✅ Reward shaping (step + final rewards)
- ✅ Real-world workflow simulation
- ✅ OpenEnv compliant API

---

## 🔁 API Endpoints

### Reset Environment

POST /reset


### Take Step

POST /step


### Debug / Test

GET /run/{task}


Examples:

/run/easy
/run/medium
/run/hard


---

## 🧪 Example Output


[START] task=hard env=incident-env model=default-agent
[STEP] step=1 action=classify_issue reward=0.15 done=false
[STEP] step=2 action=decide_action reward=0.05 done=false
[STEP] step=3 action=escalate_issue reward=0.05 done=false
[STEP] step=4 action=assign_team reward=0.65 done=true
[END] success=true steps=4 score=0.90


---

## 🏗️ Architecture


Agent → /step → Environment → Reward → Feedback loop


- `inference.py` → core logic  
- `server/app.py` → API layer  
- OpenEnv → evaluation system  

---

## 📂 Project Structure


incident-env/
├── env/
├── server/
│ └── app.py
├── inference.py
├── Dockerfile
├── pyproject.toml
└── README.md


---

## ▶️ Run Locally


python inference.py --task easy
python inference.py --task medium
python inference.py --task hard


---

## 🧠 Design Approach

- Deterministic outputs for reliable evaluation  
- Structured decision-making flow  
- Real-world applicability  

---

## 🏆 Hackathon Submission

Built for:
**Meta x PyTorch OpenEnv Hackathon**

---

## 👨‍💻 Author

**Venu (Vebnox)**  
