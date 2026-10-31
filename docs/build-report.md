# Test build report: what worked and what didn’t

Test build on an Apple Silicon Mac, October 25, 2026. End result: the full pipeline worked. Moving one task to Done changed the dashboard from Done 2 → 3 and completion 25% → 37.5%.

## What worked

- **Local app:** `python3 -m venv .venv`, install requirements, load `.env` with `set -a; source .env; set +a`, run `python3 app.py`. `/` and `/metrics` both served.
- **Notion:** a token starting with `ntn_`, the `task-board` connection added to the database, and the real database ID.
- **Kubernetes:** Pod `1/1 Running`, Service `task-board` (80 → 8000), secret `notion-secret` with two keys (32 and 50 bytes).
- **Prometheus:** ServiceMonitor selected; target `health: up`; `notion_tasks` returned three rows.
- **Grafana:** four panels working, with the bar chart on Instant + Table.

## What didn’t, and the fix

| Problem | Cause | Fix |
| --- | --- | --- |
| `brew install --cask docker` failed | Leftover from an older Docker install | Docker was already working; reinstall only if `docker version` fails |
| `brew install node` failed: `unknown install step: remove` | Homebrew older than the package | `brew update`, then `brew reinstall node` |
| `python3 -m myenv1 .venv` failed | Wrong module name | `python3 -m venv .venv` |
| `Address already in use` on 8000 | Old `python3 app.py` still running | `lsof -nP -iTCP:8000 -sTCP:LISTEN`, `kill <PID>` |
| Site unreachable after Ctrl+C | Ctrl+C stops the Flask server | Restart the app |
| Notion `401 Unauthorized` | Token had a typo in its prefix | Recopy the token (`ntn_…`) |
| Notion `404 object_not_found` | Database not shared with the connection | Add `task-board` under the database’s Connections |
| Notion `400 ... is a page, not a database` | The ID was the page containing an inline database | Use the inline database’s own ID (found by listing the page’s children) |
| Couldn’t find where to create the integration | Notion moved it | notion.so/my-integrations → Create a new connection → API token |
| Deployment used `task-board:latest`, no pull policy | Devin’s first draft | Copilot changed it to `:v1` + `IfNotPresent` |
| `port-forward 8000:8000` failed | Service listens on 80 | `port-forward svc/task-board 8080:80` |
| Misleading HTTP 200 on 8000 | Local app answered, not the cluster | Use 8080 for the cluster; stop the local app |
| 8080 unreachable | Port-forward started by Copilot had exited | Run it in a dedicated Terminal tab |
| ServiceMonitor matched nothing | Service had no labels and an unnamed port | Add `labels: app: task-board` and port `name: http` |
| Grafana `bad_data: invalid` | `{ }` typed instead of `( )` | `sum by (status) (notion_tasks)` in Code mode |
| Bar chart “No data”, then thin stripes | Range query in a bar chart | Type Instant, Format Table, X axis `status` |
| `git check-ignore` failed | Folder wasn’t a Git repo | `git init` |

## Non-blocking warnings

- Flask development-server warning
- urllib3 `NotOpenSSLWarning` (macOS LibreSSL)
- Flask’s python-dotenv suggestion (not needed; `.env` is loaded manually)
