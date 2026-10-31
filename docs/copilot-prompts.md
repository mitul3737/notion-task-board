# Copilot CLI prompts (tested)

Start Copilot in the project folder with `copilot`. Each prompt below was used in the test build.

| Stage | Prompt | What Copilot did |
| --- | --- | --- |
| 2 | Check that docker, kind, kubectl and helm are installed and tell me what's missing. | Found all four and confirmed the Docker daemon was running |
| 4 | Create a kind cluster named workshop. | Created it and switched kubectl to `kind-workshop` |
| 4 | Build the Docker image task-board:v1 and load it into the kind cluster workshop. | Checked the Dockerfile wouldn’t copy `.env`, then built and loaded the image |
| 4 | Create a Kubernetes secret notion-secret from my .env file. | Read key names only (values redacted) and created the secret |
| 4 | Open k8s/deployment.yaml and check that the container image is task-board:v1 and imagePullPolicy is IfNotPresent. Fix it if not, show me the change, then run kubectl apply -f k8s/ | Changed `:latest` to `:v1`, added the pull policy, applied, waited for rollout |
| 4 | Check the task-board pods in the default namespace. If any pod isn’t Running, find out why using kubectl describe and kubectl logs, and suggest a fix. | Reported `1/1 Running`, 0 restarts |
| 4 | Why is my task-board pod in CrashLoopBackOff? | Checked events and logs, and reported the pod was healthy instead of accepting the premise |
| 5 | Install kube-prometheus-stack with Helm as release monitoring in namespace monitoring. | Installed with `--wait` and printed Grafana access commands |
| 5 | Check the task-board Service’s labels and port name. Make sure the port is named http, then create k8s/servicemonitor.yaml for kube-prometheus-stack release "monitoring" that scrapes /metrics every 30s, apply it, and confirm the target is up. | (Suggested prompt for Stage 5) |

## Good habits to point out

- Copilot adds `--context kind-workshop` to every `kubectl` command, so it can’t touch the wrong cluster.
- It redacts `.env` values and uses `kubectl describe` (sizes only) instead of printing secrets.
- Keep `port-forward` out of Copilot. In the test, it ran `port-forward svc/task-board 8000:8000` in a detached shell; the forward failed, and a follow-up `curl` hit the leftover local app instead, returning a misleading 200.
- `/remote` shares a session to GitHub web and mobile, so helpers can follow along.
