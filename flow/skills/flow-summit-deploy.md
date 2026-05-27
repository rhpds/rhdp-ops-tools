---
name: flow-summit-deploy
description: Summit deployment -- pre-configured defaults for Red Hat Summit events
user-invocable: true
argument-hint: "day <N> <spreadsheet_path> [exclude_users]"
---

# Flow Summit Deploy

Streamlined deployment workflow pre-configured for Red Hat Summit events. Uses Summit-specific defaults to minimize configuration.

## Prerequisite Check

1. Call `flow_health` -- both `rhdp-flow-csv` and `rhdp-flow-mcp` must be available
2. If either is missing, tell the user which to install and stop

## Summit Defaults

These defaults are applied unless the user overrides:
- Catalog namespace: `babylon-catalog-event`
- Naming template: `Day {day}-Test-{title}`
- Activity: `Brand Event`
- Purpose: `Summit 2026`
- Concurrency: `12`
- Enable workshop interface: `True`
- Redirect: `True`
- White Glove: `False`

## Workflow

### Step 1: Day selection

Ask: "Which Summit day are you deploying? (e.g., Day 1, Day 3)"

### Step 2: Spreadsheet

Ask for the path to the planning spreadsheet for that day.

### Step 3: User exclusions

Ask: "Any users to exclude from deployment? (enter usernames or 'none')"

### Step 4: Transform with Summit defaults

Call `flow_transform_runbook` with Summit defaults. Show:
- Total workshops
- Auto-fixes applied
- Any warnings

### Step 5: Fix and validate

1. Call `flow_fix_csv` on the output
2. Call `flow_expand_multi_asset` on the output
3. Call `flow_upload_csv` with the final CSV
4. Call `flow_validate` with check="all"

Show combined validation results.

### Step 6: Pre-deployment checklist

Call `flow_pre_deployment_checklist` to verify:
- Backend health
- Catalog namespace matches
- Pool availability

Show pass/fail for each.

### Step 7: Deploy

If all checks pass:
1. Ask: "Ready to deploy. Dry-run first, or go live?"
2. If dry-run: call `flow_deploy` with `dry_run=true`, show manifests
3. If live: call `flow_deploy` with `dry_run=false`
4. Call `flow_deploy_status` to show initial deployment results

If checks failed, stop and show what needs to be fixed.

## Output

```
Summit Deploy: Day <N>
=======================
Workshops:    <count>
Total seats:  <count>
Validation:   <PASS/FAIL>
Deployment:   <DRY_RUN/DEPLOYED/NOT_STARTED>

Status:
  <workshop 1>: <status>
  <workshop 2>: <status>
  ...
```
