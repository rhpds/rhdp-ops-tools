---
name: flow-bulk
description: Bulk staggered workshop deployment for events and load tests
user-invocable: true
argument-hint: "<catalog_item> <count> <users_per_instance> [interval_min] [concurrency] [start_time]"
---

# Flow Bulk

Specialization of flow-deploy for bulk and staggered workshop deployments. Designed for events (Summit, workshops with many parallel sessions) and load testing.

## Prerequisite Check

1. Call `flow_health` -- if error, stop and report connectivity issue.

## Workflow

### Step 1: Select catalog item

Call `flow_catalog_items` to show available items. Ask the user to pick one.

### Step 2: Gather bulk parameters

Ask these one at a time:
- **Count**: how many workshop instances to deploy
- **Users per instance**: how many users per workshop (validate against catalog max)
- **Namespace**: base namespace for all instances
- **Interval minutes**: time between each provisioning (default 10)
- **Start time**: when to begin the first provisioning (ISO 8601 UTC)
- **Password**: shared password for all workshops
- **Concurrency**: optional, max parallel provisions (default: no limit)
- **Auto-stop hours**: default 8
- **Auto-destroy days**: default 14

### Step 3: Generate bulk CSV

Build the workshops array with the specified count, all using the same CI, namespace, and users:

```json
{
  "workshops": [
    {"ci": "<ci>", "namespace": "<namespace>", "users": <N>},
    {"ci": "<ci>", "namespace": "<namespace>", "users": <N>},
    ...
  ],
  "start_time": "<start>",
  "interval_minutes": <interval>,
  "auto_stop_hours": <hours>,
  "auto_destroy_days": <days>,
  "password": "<password>",
  "concurrency": <N>
}
```

Call `flow_generate_csv` with this input.

Show the generated CSV with a summary:

```
Bulk Deployment Plan
--------------------
Catalog Item:   <ci>
Instances:      <count>
Users/Instance: <N>
Total Users:    <count * N>
Interval:       <N> minutes
First deploy:   <start_time>
Last deploy:    <start_time + (count-1) * interval>
```

### Step 4: Upload, validate, and deploy

Follow the same flow as `flow-deploy`:
1. `flow_upload_csv` -- upload the CSV
2. `flow_validate` -- check for violations
3. `flow_deploy` with `dry_run=true` -- preview
4. Ask user to confirm
5. `flow_deploy` with `dry_run=false` -- deploy
6. `flow_deploy_status` -- show results

### Step 5: Monitor

After deployment, suggest:
> "Run `/flow-status` to monitor progress, or `/flow-qa` to verify all instances once provisioning completes."
