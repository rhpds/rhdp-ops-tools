
# Module 05 -- Event-Scale Operations

Estimated time: 30 minutes
Prerequisites: Module 01 (RHDP-Flow MCP), Module 03 (CSV Pipeline), Module 04 (Deployment Intelligence)

Capstone: simulate managing a multi-day event using all Flow skills, agents, and MCP tools together -- from runbook analysis through deployment, monitoring, and troubleshooting.

## External Dependencies

This module uses the Two-Track Dependency Pattern. It requires the full RHDP-Flow stack:

- **Flow API backend** -- a running Flow instance (local or OCP route)
- **OpenShift cluster** -- for deployment operations
- **3 MCP servers** -- rhdp-flow-mcp, rhdp-flow-csv, rhdp-flow-intel
- **Skills** -- flow-csv-pipeline, flow-event-prep, flow-summit-deploy
- **Agents** -- flow-runbook-analyzer, flow-post-deploy-monitor

If the Flow API is not reachable, the module follows the conceptual track with prepared scenarios.

## Orientation

Print this once at the start:

```
You're running the RHDP-Flow capstone: event-scale operations.
This takes about 30 minutes.

This module doesn't introduce new tools. Instead, it combines everything
from Modules 23-26 into a realistic multi-day event simulation -- the
same workflow the ops team uses during Red Hat Summit.

We'll work through:
  1. Analyze a multi-day runbook for issues (agent)
  2. Run the CSV pipeline on Day 1 (skill)
  3. Prepare all 3 days with aggregated pool demand (skill)
  4. Deploy Day 1 with Summit defaults (skill)
  5. Monitor post-deployment progress (agent)
  6. Use the event dashboard and troubleshooter

After this module you'll be able to run end-to-end event operations
using the full RHDP-Flow toolchain.

You'll need:
  - Module 01 completed (Flow MCP working)
  - Module 03 completed (CSV Pipeline working)
  - Module 04 completed (Deployment Intelligence working)
  - All 3 MCP servers: rhdp-flow-mcp, rhdp-flow-csv, rhdp-flow-intel
  - Flow skills and agents installed
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/27.started
```

## Preflight

Run these checks automatically. Show results as EXISTS/MISSING.

### Check 1: rhdp-flow-mcp server

```bash
python3 -c "import rhdp_flow_mcp" 2>/dev/null && echo "EXISTS: rhdp-flow-mcp package" || echo "MISSING: rhdp-flow-mcp -- complete Module 01 first"
```

### Check 2: rhdp-flow-csv server

```bash
python3 -c "import rhdp_flow_csv" 2>/dev/null && echo "EXISTS: rhdp-flow-csv package" || echo "MISSING: rhdp-flow-csv -- complete Module 03 first"
```

### Check 3: rhdp-flow-intel server

```bash
python3 -c "import rhdp_flow_intel" 2>/dev/null && echo "EXISTS: rhdp-flow-intel package" || echo "MISSING: rhdp-flow-intel -- complete Module 04 first"
```

### Check 4: Flow API reachable

Call `flow_health` via MCP. If status is "ok", EXISTS. If error or not available:

```
MISSING: Flow API not reachable

  Two options:

  FULL EXPERIENCE (recommended):
    Ensure the Flow API backend is running and accessible.
    Once available, re-run this module.

  CONCEPTUAL OVERVIEW:
    Continue without it. You'll learn the full event workflow
    but won't be able to execute live deployments.
```

### Check 5: Skills available

```bash
found=0
for skill in flow-csv-pipeline flow-event-prep flow-summit-deploy; do
  if find . ~/.claude -name "$skill.md" -path "*/skills/*" 2>/dev/null | grep -q .; then
    found=$((found + 1))
  fi
done
if [ "$found" -eq 3 ]; then
  echo "EXISTS: All 3 event skills installed"
else
  echo "MISSING: $((3 - found)) event skills not found -- install rhdp-flow-skills"
fi
```

### Check 6: Agents available

```bash
found=0
for agent in flow-runbook-analyzer flow-post-deploy-monitor; do
  if find . ~/.claude -name "$agent.md" -path "*/agents/*" 2>/dev/null | grep -q .; then
    found=$((found + 1))
  fi
done
if [ "$found" -eq 2 ]; then
  echo "EXISTS: Both event agents installed"
else
  echo "MISSING: $((2 - found)) event agents not found -- install rhdp-flow-agents"
fi
```

Print summary: how many checks passed, what needs to be done.

If Flow API is MISSING, tell the user they are on the conceptual track. If MCP servers are MISSING, direct them to complete the prerequisite modules first.

---

## Step 1 -- Analyze the runbook (Agent)

**Goal:** Use the `flow-runbook-analyzer` agent to review a multi-day event spreadsheet before any transformation happens.

### The scenario

You are the ops lead for a 3-day event. Here is the planning spreadsheet:

**Day 1 (Tuesday):**

```csv
Lab Code,Title,Session Date,Session Start,Attendees,Namespace,CI
LB3001,RHEL Image Mode,2026-06-16,09:00:00,40,user-klee-redhat-com,summit-2026.lb3001-rhel-imagemode
LB3002,OpenShift Virtualization,2026-06-16,09:00:00,35,user-mchen-redhat-com,summit-2026.lb3002-ocp-virt
LB3003,Ansible Lightspeed + RHEL Image Mode,2026-06-16,13:00:00,25,user-pgarcia-redhat-com,summit-2026.lb3003-ansible-lightspeed,summit-2026.lb3003-rhel-imagemode
LB3004,OpenShift AI,2026-06-16,13:00:00,30,user-sjones-redhat-com,summit-2026.lb3004-ocp-ai
LB3005,AAP + EDA,2026-06-16,16:00:00,20,user-tbrown-redhat-com,summit-2026.lb3005-aap-eda
```

**Day 2 (Wednesday):**

```csv
Lab Code,Title,Session Date,Session Start,Attendees,Namespace,CI
LB3010,OpenShift Virtualization,2026-06-17,09:00:00,35,user-mchen-redhat-com,summit-2026.lb3010-ocp-virt
LB3011,RHEL Image Mode,2026-06-17,09:00:00,40,user-klee-redhat-com,summit-2026.lb3011-rhel-imagemode
LB3012,Ansible Automation Platform,2026-06-17,09:00:00,30,user-asmith-redhat-com,summit-2026.lb3012-aap
LB3013,OpenShift AI,2026-06-17,13:00:00,30,user-sjones-redhat-com,summit-2026.lb3013-ocp-ai
LB3014,Podman Desktop,2026-06-17,13:00:00,25,user-jdoe-redhat-com,summit-2026.lb3014-podman
LB3015,RHEL Image Mode,2026-06-17,13:00:00,40,user-klee-redhat-com,summit-2026.lb3015-rhel-imagemode
LB3016,Trusted Software Supply Chain,2026-06-17,16:00:00,20,user-rwilson-redhat-com,summit-2026.lb3016-tssc
LB3017,AAP + EDA + RHEL Image Mode,2026-06-17,16:00:00,25,user-tbrown-redhat-com,summit-2026.lb3017-aap-eda,summit-2026.lb3017-rhel-imagemode
```

**Day 3 (Thursday):**

```csv
Lab Code,Title,Session Date,Session Start,Attendees,Namespace,CI
LB3020,RHEL Image Mode,2026-06-18,09:00:00,50,user-klee-redhat-com,summit-2026.lb3020-rhel-imagemode
LB3021,OpenShift AI,2026-06-18,09:00:00,40,user-sjones-redhat-com,summit-2026.lb3021-ocp-ai
LB3022,Ansible Automation Platform,2026-06-18,09:00:00,35,user-asmith-redhat-com,summit-2026.lb3022-aap
LB3023,OpenShift Virtualization,2026-06-18,13:00:00,35,user-mchen-redhat-com,summit-2026.lb3023-ocp-virt
LB3024,Podman Desktop,2026-06-18,13:00:00,30,user-jdoe-redhat-com,summit-2026.lb3024-podman
LB3025,RHEL Image Mode,2026-06-18,16:00:00,45,user-klee-redhat-com,summit-2026.lb3025-rhel-imagemode
```

### Run the runbook analyzer

Ask Claude to analyze the multi-day runbook or invoke the `flow-runbook-analyzer` agent pattern.

The agent should review:
- **Workshop count per day**: Day 1 has 5 workshops (2 multi-asset), Day 2 has 8 workshops (1 multi-asset), Day 3 has 6 workshops
- **Multi-asset candidates**: LB3003 and LB3017 have multiple CI values and need expansion
- **Pool demand**: RHEL Image Mode appears on all 3 days with high seat counts (aggregate demand is the largest)
- **Namespace conflicts**: check if any namespace is reused across days without cleanup
- **Facilitator load**: user-klee-redhat-com runs RHEL Image Mode multiple times across days -- flag as high load

### Review the analysis

Walk through the agent's findings:
- Total workshops across all 3 days
- Multi-asset rows that need expansion before processing
- Peak pool demand by catalog item
- Any scheduling conflicts or concerns
- Facilitator workload flags

### Verification

The runbook analyzer identifies the multi-asset rows, calculates aggregate demand, and flags potential issues before any transformation begins.

---

## Step 2 -- Run the CSV pipeline (Skill)

Skip if on the conceptual track. Skipped: requires rhdp-flow-csv.

**Goal:** Process Day 1's spreadsheet through the full CSV pipeline using the `flow-csv-pipeline` skill.

### Run the pipeline on Day 1

Invoke the `flow-csv-pipeline` skill with the Day 1 spreadsheet from Step 1.

Event config:

```json
{
  "timezone": "US/Eastern",
  "target_timezone": "UTC",
  "catalog_namespace": "babylon-catalog-event",
  "naming_template": "Summit Boston Day 1-{title}"
}
```

### Walk through the pipeline stages

The skill runs four stages in sequence:

1. **Transform**: converts the messy planning spreadsheet to Flow-compliant CSV
   - Column renaming (Lab Code dropped, Title mapped to naming, etc.)
   - Date/time merging and timezone conversion
   - Missing fields generated with defaults

2. **Fix**: validates and auto-fixes common issues
   - Date format corrections
   - Missing optional columns added
   - Value range checks

3. **Expand**: detects and splits multi-asset rows
   - LB3003 has two CI values -- splits into 2 rows
   - Each expanded row gets its own CI and preserves other fields

4. **Validate**: final check before the CSV is ready for deployment
   - All required columns present
   - Date formats correct
   - No duplicate rows

### Review the pipeline summary

The skill produces a summary showing:
- Rows in -> rows out (5 -> 6 after expansion)
- Fixes applied at each stage
- Warnings or errors that need manual attention

### Verification

The pipeline completes all 4 stages and produces a clean, deployment-ready CSV with 6 rows (original 5 plus 1 from multi-asset expansion).

---

## Step 3 -- Prepare multi-day event (Skill)

Skip if on the conceptual track. Skipped: requires Flow API.

**Goal:** Use the `flow-event-prep` skill to process all 3 days and generate an aggregated readiness report.

### Run event preparation

Invoke the `flow-event-prep` skill with all 3 days' spreadsheets and the event config:

```json
{
  "event_name": "Summit Boston 2026",
  "timezone": "US/Eastern",
  "target_timezone": "UTC",
  "catalog_namespace": "babylon-catalog-event",
  "days": ["Day 1", "Day 2", "Day 3"]
}
```

### Review the aggregated output

The skill produces:

**Per-day summary:**
- Day 1: 5 workshops (6 after expansion), 150 total seats
- Day 2: 8 workshops (9 after expansion), 245 total seats
- Day 3: 6 workshops, 235 total seats

**Aggregated pool demand:**
| Catalog Item | Day 1 | Day 2 | Day 3 | Peak |
|-------------|-------|-------|-------|------|
| RHEL Image Mode | 40 | 80 | 95 | 95 |
| OpenShift Virtualization | 35 | 35 | 35 | 35 |
| OpenShift AI | 30 | 30 | 40 | 40 |
| Ansible/AAP | 25 | 55 | 35 | 55 |
| Podman Desktop | 0 | 25 | 30 | 30 |
| Others | 20 | 20 | 0 | 20 |

**Readiness flags:**
- RHEL Image Mode has the highest aggregate demand -- confirm pool capacity
- Day 2 has the most concurrent sessions (3 at 09:00)
- Multi-asset workshops on Day 1 and Day 2 need expansion before deployment

### Verification

The event prep skill processes all 3 days and produces a pool demand report that identifies RHEL Image Mode as the highest-demand catalog item.

---

## Step 4 -- Deploy with Summit defaults (Skill)

Skip if on the conceptual track. Skipped: requires Flow API.

**Goal:** Use the `flow-summit-deploy` skill for Day 1's deployment with Summit-specific defaults.

### Run deployment

Invoke the `flow-summit-deploy` skill with the pipeline output from Step 2.

The skill runs a pre-deployment checklist:
- CSV validated (from pipeline)
- Pool capacity checked for each catalog item
- Namespace conflicts checked
- Dry-run mode confirmed

### Pre-deployment checklist

Walk through each check:

| Check | Status | Details |
|-------|--------|---------|
| CSV valid | PASS | 6 rows, all required columns present |
| Pool capacity | CHECK | RHEL Image Mode needs 40 seats -- verify pool |
| Namespace conflicts | PASS | No namespace reuse detected |
| Facilitator schedule | WARN | user-klee has back-to-back sessions |

### Dry-run

The skill executes a dry-run deployment:
- Simulates all 6 workshop deployments
- Reports what would be created, modified, or skipped
- No actual resources provisioned

Walk through the dry-run output:
- 6 workshops would be deployed
- Estimated provisioning time per workshop
- Total cluster resources required

### Live deployment (conceptual)

In a real event, after dry-run succeeds:
1. The skill prompts for confirmation
2. Deploys workshops in the order specified by the CSV
3. Reports progress as each workshop starts provisioning

For this module, stop at the dry-run stage unless on a dedicated training cluster.

### Verification

The pre-deployment checklist completes and the dry-run succeeds for all 6 workshops.

---

## Step 5 -- Monitor post-deployment (Agent)

Skip if on the conceptual track. Skipped: requires Flow API.

**Goal:** Use the `flow-post-deploy-monitor` agent to track deployment progress after workshops go live.

### Initial status check

After deployment (or simulated deployment), invoke the `flow-post-deploy-monitor` agent.

The agent checks initial state:
- Some workshops in PROVISIONING state
- Some already READY
- Any in ERROR state

Example initial output:

```
Post-Deployment Status (T+5 minutes):

  READY:        2/6  (LB3001, LB3005)
  PROVISIONING: 3/6  (LB3002, LB3003a, LB3004)
  ERROR:        1/6  (LB3003b -- multi-asset child)

  Estimated time to all-ready: ~15 minutes
  Action needed: LB3003b failed provisioning -- investigate
```

### Progress tracking

The agent can be re-invoked to track progress over time:

```
Post-Deployment Status (T+15 minutes):

  READY:        5/6  (LB3001, LB3002, LB3003a, LB3004, LB3005)
  ERROR:        1/6  (LB3003b -- retrying)

  Progress: 83% ready
  Action needed: LB3003b retry in progress
```

### Ghost detection

The agent checks for ghost deployments -- workshops that exist in the cluster but are not in the current schedule:

```
Ghost Detection:
  Found 0 ghost deployments -- cluster is clean
```

### QA verification

The agent runs QA checks on READY workshops:

```
QA Status:
  LB3001 RHEL Image Mode:       QA PASS
  LB3002 OCP Virtualization:    QA PASS
  LB3003a Ansible Lightspeed:   QA PASS
  LB3004 OpenShift AI:          QA PASS
  LB3005 AAP + EDA:             QA PASS

  5/5 ready workshops pass QA
```

### Verification

The monitoring agent tracks deployment progress, detects issues, and runs QA on ready workshops.

---

## Step 6 -- Health dashboard and troubleshooting

**Goal:** Use `flow_event_dashboard` for the aggregate view and `flow_troubleshoot` to diagnose and fix an issue.

### Event dashboard

Call `flow_event_dashboard` (from rhdp-flow-intel) to get the aggregate event health view.

The dashboard shows:
- **Event overview**: Summit Boston 2026, Day 1 of 3
- **Deployment health**: 5/6 ready, 1 in error
- **Pool utilization**: capacity vs demand per catalog item
- **QA summary**: 5/5 ready workshops passing QA
- **Alerts**: LB3003b provisioning failure

Walk through the dashboard sections and how they connect to the individual tools used in previous steps.

### Troubleshoot the failing workshop

Call `flow_troubleshoot` on the failing workshop (LB3003b):

The troubleshooter runs a diagnosis:
1. **Status check**: confirms the workshop is in ERROR state
2. **Error analysis**: identifies the root cause (e.g., pool exhaustion for the catalog item, namespace conflict, or provisioning timeout)
3. **Fix suggestion**: proposes a specific action (e.g., retry deployment, scale pool, change namespace)
4. **Remediation**: executes the fix if approved

Walk through the full cycle:
- Diagnosis reveals the issue
- Fix is proposed with explanation
- Fix is applied (or simulated)
- Re-check confirms the workshop is now PROVISIONING or READY

### Verification

The event dashboard provides a single-pane view of event health, and the troubleshooter completes a full diagnose-fix-verify cycle.

---

## Verification

Confirm understanding of the full event-scale workflow:

```bash
PASS=0
TOTAL=5

# These are conceptual checks -- the user confirms understanding
echo "Answer these questions to verify your understanding:"
echo ""
echo "1. What are the CSV pipeline stages in order?"
echo "   (Expected: transform -> fix -> expand -> validate)"
echo ""
echo "2. What does the event prep skill add beyond the CSV pipeline?"
echo "   (Expected: multi-day aggregation, pool demand report, readiness flags)"
echo ""
echo "3. What does the deployment monitor track after workshops go live?"
echo "   (Expected: provisioning progress, ghost detection, QA verification)"
echo ""
echo "4. How do you diagnose a failing workshop?"
echo "   (Expected: flow_troubleshoot -- diagnosis, fix suggestion, remediation)"
echo ""
echo "5. Where do you get the single-pane event health view?"
echo "   (Expected: flow_event_dashboard)"
```

Ask the user to answer each question. Mark each as PASS or FAIL based on their response.

If all pass, print:

```
All checks passed. You understand the full event-scale operations workflow.
```

If any fail, explain the correct answer and re-ask.

---

## Challenge

```
You are the ops lead for a 3-day event starting tomorrow. You have
planning spreadsheets for all 3 days (from Step 1 above).

Walk through the complete ops workflow:

  1. Analyze Day 1's runbook for potential issues
  2. Run the CSV pipeline on Day 1
  3. Check pool availability for Day 1's workshops
  4. Deploy Day 1 (dry-run)
  5. Monitor the deployment and report status
  6. Run the event dashboard

Tell me:
  1. What issues did the runbook analyzer find?
  2. How many auto-fixes did the CSV pipeline apply?
  3. Are pools sufficient for Day 1?
  4. What does the event dashboard show?
```

## Challenge Verification

Check the user's answers:

1. **Runbook analyzer findings**: Should identify LB3003 as a multi-asset workshop needing expansion, flag user-klee-redhat-com as high facilitator load across days, and note that RHEL Image Mode has the highest aggregate demand across all 3 days.

2. **CSV pipeline auto-fixes**: The exact count depends on tool output. The user should identify date format conversions (Session Date + Session Start merged to DD/MM/YYYY HH:MM), column remapping (Attendees to Users, etc.), and multi-asset expansion (LB3003 splits into 2 rows, giving 6 total from 5 original).

3. **Pool sufficiency**: The user should report whether pool capacity meets demand for each catalog item on Day 1. RHEL Image Mode (40 seats) and OCP Virtualization (35 seats) are the largest demands.

4. **Event dashboard**: Should show Day 1 deployment health (workshops deployed or dry-run'd), pool utilization, QA summary, and any alerts. The user should be able to identify the key metrics.

If the user's answers demonstrate understanding of the workflow, write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/27.done
```

Then print:

```
Module 05 complete.

You've practiced the full event-scale operations workflow: analyzing
runbooks, preparing CSVs, deploying with Summit defaults, monitoring
deployments, and troubleshooting issues.

This is the capstone of the RHDP-Flow integration. You now have
3 MCP servers (25 tools), 9 skills, and 5 agents available for
workshop automation.

For real events, start with /flow-event-prep for multi-day preparation
or /flow-summit-deploy for single-day Summit deployments.

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
