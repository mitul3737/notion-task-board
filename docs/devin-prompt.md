# Devin Desktop prompt

Open an empty folder in Devin Desktop and paste:

> Build a minimal Python Flask app. It reads tasks from a Notion database using the NOTION_TOKEN and NOTION_DATABASE_ID environment variables and the Notion-Version 2022-06-28 header. Each task has a Name (title) and Status (select). The `/` route shows tasks grouped by status in a simple HTML page. The `/metrics` route exposes Prometheus metrics using prometheus_client: a gauge `notion_tasks{status}` with the count per status, refreshed from Notion every 30 seconds, and a counter `app_requests_total`. The app listens on port 8000. Add requirements.txt, a Dockerfile that copies only requirements.txt and app.py, and Kubernetes manifests in k8s/: a Deployment using image task-board:v1 with imagePullPolicy IfNotPresent, reading both env vars from a Secret named notion-secret; and a Service named task-board with metadata label app: task-board, selector app: task-board, and one port named http (port 80, targetPort 8000).

## Check before building the image

- The Dockerfile copies only `requirements.txt` and `app.py`, so `.env` stays out of the image.
- The Deployment uses `image: task-board:v1` and `imagePullPolicy: IfNotPresent`. In the test build, Devin’s first draft used `task-board:latest` with no pull policy.
- The Service has the label `app: task-board` and a port named `http`. The first draft had neither, which stopped Prometheus from finding it.
