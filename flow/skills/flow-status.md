---
name: flow-status
description: Workshop status overview -- deployments, QA results, and pool availability
user-invocable: true
argument-hint: "(no arguments -- pulls deployments, QA results, and pool availability into one dashboard)"
---

# Flow Status

Pull deployment results, QA results, and pool availability into a single status summary. Good for morning standups or pre-event checks.

## Prerequisite Check

1. Call `flow_health` -- if error, stop and report connectivity issue.

## Workflow

### Step 1: Gather data

Make these calls in parallel (they are independent):

1. `flow_deploy_status` -- deployment results
2. `flow_qa_results` -- QA check results
3. `flow_pools` -- resource pool availability

### Step 2: Present status dashboard

Format as a single summary:

```
RHDP-Flow Status
=================

Backend: <status> | Cluster: <cluster_url>

Deployments
-----------
Total:    <N> workshops
Running:  <N>
Failed:   <N>
Pending:  <N>

QA Results
----------
Last run: <timestamp or "no results">
Passed:   <N>/<total>
Issues:   <list any failures briefly>

Resource Pools
--------------
<pool_name>:
  Ready:         <N>
  Claimed:       <N>
  Provisioning:  <N>
```

### Step 3: Flag concerns

If any of these conditions are true, add a "Needs Attention" section:
- Any deployments in failed state
- QA failures exist
- Pool availability is below 5 ready instances
- No QA results exist (QA hasn't been run)

```
Needs Attention
---------------
- <N> failed deployments -- run /flow-qa for details
- QA has not been run -- consider running /flow-qa
- Pool <name> has only <N> ready instances
```
