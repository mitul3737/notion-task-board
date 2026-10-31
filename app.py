"""Notion Task Board: reads tasks from a Notion database, shows them grouped by
status, and exposes task counts as Prometheus metrics.

Reference version for the workshop. Env vars: NOTION_TOKEN, NOTION_DATABASE_ID.
"""
import os
import threading
import time
from collections import defaultdict

import requests
from flask import Flask, Response, render_template_string
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
NOTION_VERSION = "2022-06-28"  # classic database query endpoint
REFRESH_SECONDS = 30
STATUSES = ["To Do", "In Progress", "Done"]

app = Flask(__name__)

NOTION_TASKS = Gauge("notion_tasks", "Number of Notion tasks by status", ["status"])
APP_REQUESTS = Counter("app_requests_total", "Total HTTP requests")

_tasks: dict[str, list[str]] = {s: [] for s in STATUSES}
_lock = threading.Lock()


def fetch_tasks() -> dict[str, list[str]]:
    """Query every page of the Notion database and group task names by status."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    grouped: dict[str, list[str]] = defaultdict(list)
    payload: dict = {}
    while True:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for page in data["results"]:
            props = page["properties"]
            title = "".join(t["plain_text"] for t in props["Name"]["title"]) or "(untitled)"
            select = props["Status"]["select"]
            grouped[select["name"] if select else "No status"].append(title)
        if not data.get("has_more"):
            break
        payload = {"start_cursor": data["next_cursor"]}
    return grouped


def refresh_loop() -> None:
    """Every REFRESH_SECONDS, re-read Notion and update the gauge."""
    global _tasks
    while True:
        try:
            grouped = fetch_tasks()
            with _lock:
                _tasks = {s: grouped.get(s, []) for s in STATUSES}
            for status in STATUSES:
                NOTION_TASKS.labels(status=status).set(len(grouped.get(status, [])))
        except requests.RequestException as exc:
            app.logger.error("Notion query failed: %s", exc)
        time.sleep(REFRESH_SECONDS)


PAGE = """
<!doctype html><title>Task Board</title>
<style>body{font-family:system-ui;margin:2rem}h2{margin-top:1.5rem}</style>
<h1>Task Board</h1>
{% for status, items in tasks.items() %}
  <h2>{{ status }} ({{ items|length }})</h2>
  <ul>{% for t in items %}<li>{{ t }}</li>{% endfor %}</ul>
{% endfor %}
"""


@app.before_request
def count_request() -> None:
    APP_REQUESTS.inc()


@app.route("/")
def index():
    with _lock:
        tasks = dict(_tasks)
    return render_template_string(PAGE, tasks=tasks)


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    threading.Thread(target=refresh_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8000)
