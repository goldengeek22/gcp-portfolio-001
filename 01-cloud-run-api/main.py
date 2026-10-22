import hashlib
import json
import os
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException
from google.cloud import firestore
from pydantic import BaseModel

app = FastAPI(title="Tasks API")
db = firestore.Client()
tasks = db.collection("tasks")
API_KEY = os.environ.get("API_KEY", "")


class TaskIn(BaseModel):
    title: str
    done: bool = False


def log(severity: str, **fields):
    # One JSON line on stdout = one structured log entry in Cloud Logging
    print(json.dumps({"severity": severity, **fields}), flush=True)


def require_key(key: str):
    if not API_KEY or key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")


@app.get("/health")
def health():
    return {"status": "ok", "revision": os.environ.get("K_REVISION", "local")}


@app.get("/tasks")
def list_tasks():
    docs = tasks.order_by("created_at").limit(50).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn, x_api_key: str = Header(default="")):
    require_key(x_api_key)
    data = task.model_dump() | {"created_at": datetime.now(timezone.utc)}
    _, ref = tasks.add(data)
    log("INFO", event="task_created", task_id=ref.id)   # used by project 5
    return {"id": ref.id, **data}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str, x_api_key: str = Header(default="")):
    require_key(x_api_key)
    tasks.document(task_id).delete()


@app.get("/hash")
def hash_work(rounds: int = 100_000):
    # CPU-heavy on purpose: used to trigger autoscaling in project 4
    h = b"seed"
    for _ in range(min(rounds, 2_000_000)):
        h = hashlib.sha256(h).digest()
    return {"rounds": rounds, "digest": h.hex()[:16]}


@app.get("/debug/error")
def debug_error(x_api_key: str = Header(default="")):
    # Deliberate 500 for testing alerts in project 5
    require_key(x_api_key)
    log("ERROR", event="forced_error")
    raise HTTPException(status_code=500, detail="forced error for alert testing")
