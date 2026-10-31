# Grafana panels

Create a dashboard: **Dashboards → New → New dashboard → Auto grid → Panel**. For each panel, choose the **Prometheus** data source, switch the query editor to **Code**, and paste the query exactly.

| Panel title | Visualization | Query | Settings |
| --- | --- | --- | --- |
| Tasks by status | Bar chart | `sum by (status) (notion_tasks)` | Query options: Type **Instant**, Format **Table**. Bar chart: X axis **status** |
| Done | Stat | `notion_tasks{status="Done"}` | None |
| Completion % | Gauge | `notion_tasks{status="Done"} / scalar(sum(notion_tasks)) * 100` | Standard options: Unit **Percent (0-100)**, Min 0, Max 100 |
| App requests per minute | Time series | `rate(app_requests_total[1m]) * 60` | Legend: Custom `requests`. Standard options: Min 0 |

Dashboard: time range **Last 15 minutes**, auto-refresh **10s**, save as **Notion Task Board**.

## Notes

- `( )` groups and calls functions; `{ }` filters by label. Mixing them up gives `bad_data: invalid`.
- The request line sits near 2 per minute with no visitors: that’s Prometheus requesting `/metrics` every 30 seconds.
- If a panel shows **No data**, test the query in **Explore** (compass icon). If Explore shows data, use **Add → Add to dashboard** from there.
- After building, export the dashboard (**Export → Export as JSON**) and save it here as `grafana/dashboard.json` so others can import it.
