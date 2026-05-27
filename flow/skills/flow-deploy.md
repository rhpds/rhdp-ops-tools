---
name: flow-deploy
description: Guided workshop deployment -- CSV generation, validation, dry-run, and deploy
user-invocable: true
argument-hint: "<catalog_item> <namespace> <users> [start_time] [password] [auto_stop_hours] [auto_destroy_days]"
---

# Flow Deploy

Guided workflow for deploying workshops through RHDP-Flow.

## Prerequisite Check

Before starting, verify the MCP server is reachable:

1. Call `flow_health`
2. If status is "error", stop and tell the user:
   > Flow backend is not reachable. Check that `rhdp-flow-mcp` is installed and `FLOW_API_URL` is set correctly.
3. If status is "ok", proceed.

## Workflow

Walk the user through deployment one question at a time. Do not present all questions at once.

### Step 1: Select catalog item

Call `flow_catalog_items` to get the list. Present available items with their descriptions and user limits. Ask the user to pick one.

### Step 2: Gather deployment parameters

Ask these one at a time:
- **Namespace**: what namespace to deploy into (e.g., `user-alice`)
- **Users**: how many users (validate against the catalog item's max from Step 1)
- **Start time**: when to provision (ISO 8601 format, UTC)
- **Password**: workshop password
- **Auto-stop hours**: default 8
- **Auto-destroy days**: default 14

### Step 3: Generate CSV

Call `flow_generate_csv` with the collected parameters as a JSON string:

```json
{
  "workshops": [{"ci": "<selected_ci>", "namespace": "<namespace>", "users": <count>}],
  "start_time": "<start_time>",
  "auto_stop_hours": <hours>,
  "auto_destroy_days": <days>,
  "password": "<password>"
}
```

Show the generated CSV to the user for review.

### Step 4: Upload and validate

1. Call `flow_upload_csv` with the generated CSV
2. Call `flow_validate` with check="all"
3. If validation finds issues, show them and ask the user if they want to fix and regenerate
4. If validation passes, proceed

### Step 5: Dry-run

1. Call `flow_deploy` with `dry_run=true`
2. Show the dry-run results (manifests that would be applied)
3. Ask: "Deploy for real?"

### Step 6: Live deploy

1. Call `flow_deploy` with `dry_run=false`
2. Call `flow_deploy_status` to get results
3. Present a summary: how many workshops deployed, any failures

## Output

Present final results as:

```
Deployment Summary
------------------
Catalog Item: <ci>
Namespace:    <namespace>
Users:        <count>
Status:       <success/partial/failed>
Deployed:     <N> workshops
Failed:       <N> workshops (if any)
```
