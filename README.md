# Incident Env

📌 Description
This environment simulates real-world customer incident resolution workflows where AI agents must classify, prioritize, and resolve issues through multi-step decision-making.

This environment simulates LLM-like reasoning using deterministic logic for stable evaluation.

It incorporates realistic constraints such as user sentiment, task sequencing, and workflow dependencies, enforcing optimal action ordering and penalizing inefficient or incorrect decisions.

The environment is designed to evaluate agent performance in enterprise support scenarios, including classification, escalation, and resolution under uncertainty.

## Action Space
- `classify_issue`
- `reply_user`
- `escalate_issue`
- `assign_team`
- `request_more_info`
- `ignore`

## Observation Space (Pydantic Mapped)
- `issue_type`
- `user_mood`
- `customer_tier`
- `crm_status`
- `conversation_history`

## Tasks
1. **EASY**: `classify issue correctly`
2. **MEDIUM**: `classify + respond correctly`
3. **HARD**: `handle angry customer + escalate properly + resolve issue`

## Setup Instructions

```bash
docker build -t incident-env .
docker run incident-env python inference.py --task easy
```
Alternatively run natively:
```bash
pip install -r requirements.txt
python inference.py --task easy
```

---
*Built by Vebnox (vebnox.com) — AI & Automation Solutions*
