---
name: flow-report
description: Generate deployment and QA reports for stakeholders
user-invocable: true
argument-hint: "slack | email | summary"
---

# Flow Report

Aggregate deployment and QA data into a formatted summary suitable for Slack, email, or stakeholder updates.

## Prerequisite Check

1. Call `flow_health` -- if error, stop and report connectivity issue.

## Workflow

### Step 1: Gather all data

Make these calls to collect the full picture:

1. `flow_health` -- backend and cluster status
2. `flow_deploy_status` -- deployment results
3. `flow_qa_results` -- QA check results
4. `flow_pools` -- resource pool availability

### Step 2: Ask for report format

Ask the user:
- **Slack**: concise format suitable for posting in a Slack channel
- **Email**: more detailed format with sections
- **Summary**: one-paragraph executive summary

Default to Slack format if not specified.

### Step 3: Generate report

**Slack format:**

```
*RHDP Workshop Status Report*
_Generated: <date/time>_

*Cluster:* <cluster_url> (<status>)
*Deployments:* <N> total | <N> running | <N> failed
*QA Pass Rate:* <N>/<total> (<percentage>%)
*Pool Capacity:* <ready> ready, <claimed> claimed

<if failures>
*Issues:*
- <failure 1>
- <failure 2>
</if>
```

**Email format:**

```
RHDP Workshop Status Report
============================
Date: <date/time>
Cluster: <cluster_url>

Deployment Summary
------------------
Total workshops: <N>
Running:         <N>
Failed:          <N>
Pending:         <N>

Workshop Details:
<table of workshops with status>

QA Summary
----------
Checks run:    <N>
Passed:        <N>
Failed:        <N>
Pass rate:     <percentage>%

Failed checks:
<list of failures with details>

Resource Pools
--------------
<pool details>

Recommendations
---------------
<actionable next steps based on current state>
```

**Summary format:**

A single paragraph summarizing the key numbers and any urgent issues.

### Step 4: Offer export

Ask:
> "Would you like to export the raw results as CSV? Use `flow_export_results` for deployment data or student data."
