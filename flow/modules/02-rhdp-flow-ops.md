
# Module 02 — RHDP-Flow Ops

Estimated time: 15 minutes
Prerequisites: Module 01 (RHDP-Flow MCP installed and configured)

Use Flow skills and agents for daily workshop operations -- status checks, QA verification, CSV validation, operations, and pre-event readiness audits.

## Quick Setup (skip the walkthrough)

If you already have Module 01 done and just want the skills and agents:

1. Install the skills plugin: copy `rhdp-flow-skills/skills/` into your project
2. Install the agents plugin: copy `rhdp-flow-agents/agents/` into your project
3. Verify: ask Claude "workshop status" -- it should use the `flow-status` skill
4. Verify: ask Claude "validate this CSV" with a sample CSV -- it should use the `flow-csv-validator` agent

Skip to the [Challenge](#challenge) for hands-on practice.

## External Dependencies

This module depends on services outside your local environment:

- **rhdp-flow-mcp** -- the MCP server must be installed and returning status "ok" from `flow_health`
- **RHDP-Scheduler repo** -- local clone of `rhpds/rhpds-utils` with latest `main` (source at `RHDP-Scheduler/`)
- **OCP authentication** -- you must be logged in with `oc login` using your personal ephemeral token (the Flow API runs on the OCP cluster)
- **Deployed workshops** -- Steps 2-5 work best with active deployments to inspect

## Orientation

Print this once at the start:

```
You're learning the RHDP-Flow skills and agents for daily workshop operations.
This takes about 15 minutes.

Skills are guided workflows that walk you through common tasks:
  - flow-deploy: end-to-end workshop deployment
  - flow-qa: QA verification with fix suggestions
  - flow-ops: lock, extend, scale workshops
  - flow-status: deployment dashboard
  - flow-bulk: staggered bulk deployments
  - flow-report: stakeholder reports

Agents are analytical reviewers:
  - flow-csv-validator: catches CSV errors before upload
  - flow-deployment-auditor: finds health issues in deployments
  - flow-pre-event-checklist: go/no-go readiness check

After this module you'll use these daily for workshop operations.

You'll need:
  - Module 01 completed (Flow MCP working)
  - oc login to the target OCP cluster (personal ephemeral token)
  - rhdp-flow-skills installed
  - rhdp-flow-agents installed
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/24.started
```

## Preflight

Run these checks automatically. Show results as EXISTS/MISSING.

### Check 1: Flow MCP server configured

```bash
python3 -c "import rhdp_flow_mcp" 2>/dev/null && echo "EXISTS: rhdp-flow-mcp package" || echo "MISSING: rhdp-flow-mcp -- complete Module 01 first"
```

### Check 2: RHDP-Scheduler repo up to date

```bash
REPO_DIR="$HOME/repos/rhpds-utils"
if [ ! -d "$REPO_DIR/RHDP-Scheduler" ]; then
  echo "MISSING: rhpds-utils repo not found -- run 'git clone git@github.com:rhpds/rhpds-utils.git $REPO_DIR'"
else
  cd "$REPO_DIR"
  git fetch origin main --quiet 2>/dev/null
  LOCAL=$(git rev-parse HEAD 2>/dev/null)
  REMOTE=$(git rev-parse origin/main 2>/dev/null)
  if [ "$LOCAL" = "$REMOTE" ]; then
    echo "EXISTS: RHDP-Scheduler up to date ($(git log -1 --format='%h %s' 2>/dev/null))"
  else
    BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)
    echo "EXISTS: RHDP-Scheduler found but ${BEHIND} commits behind -- run 'cd $REPO_DIR && git pull origin main'"
  fi
fi
```

### Check 3: OCP authentication

```bash
oc whoami >/dev/null 2>&1 && echo "EXISTS: logged in as $(oc whoami) on $(oc whoami --show-server)" || echo "MISSING: not logged in -- run 'oc login --token=sha256~<token> --server=https://api.<cluster>:6443'"
```

### Check 4: Flow backend reachable

Call `flow_health` via MCP. If status is "ok", EXISTS. If error, MISSING -- check that your `oc login` token hasn't expired.

### Check 5: Skills installed

```bash
found=0
for skill in flow-deploy flow-qa flow-ops flow-status flow-bulk flow-report; do
  if find . ~/.claude -name "$skill.md" -path "*/skills/*" 2>/dev/null | grep -q .; then
    found=$((found + 1))
  fi
done
if [ "$found" -eq 6 ]; then
  echo "EXISTS: All 6 flow skills installed"
else
  echo "MISSING: $((6 - found)) flow skills not found -- install rhdp-flow-skills"
fi
```

### Check 6: Agents installed

```bash
found=0
for agent in flow-csv-validator flow-deployment-auditor flow-pre-event-checklist; do
  if find . ~/.claude -name "$agent.md" -path "*/agents/*" 2>/dev/null | grep -q .; then
    found=$((found + 1))
  fi
done
if [ "$found" -eq 3 ]; then
  echo "EXISTS: All 3 flow agents installed"
else
  echo "MISSING: $((3 - found)) flow agents not found -- install rhdp-flow-agents"
fi
```

Print summary: how many checks passed, what needs to be done.

---

## Step 1 — Workshop status dashboard

**Goal:** Get a complete status overview using the `flow-status` skill.

### Run the skill

Ask Claude: "what's the workshop status?" or "show me what's deployed"

Expected: Claude uses the `flow-status` skill to pull deployment results, QA data, and pool availability into a single dashboard.

Walk through the output:
- **Backend status**: confirms connectivity
- **Deployments**: running, failed, pending counts
- **QA Results**: last run time, pass rate
- **Pool capacity**: ready, claimed, provisioning
- **Needs Attention**: any items flagged for follow-up

### Verification

The status dashboard renders with all three data sections populated.

---

## Step 2 — QA verification

**Goal:** Run QA checks and interpret the results.

### Run QA

Ask Claude: "run QA on the workshops" or "check workshop health"

Expected: Claude uses the `flow-qa` skill, asks which QA type to run, executes, and presents pass/fail results.

### Interpret results

Walk through the output:
- **PASS**: check succeeded, workshop is healthy
- **FAIL**: check failed, with a specific fix suggestion
- **Total checks vs passed**: the overall pass rate

### Verification

QA results show pass/fail status with actionable fix suggestions for any failures.

---

## Step 3 — CSV validation agent

**Goal:** Use the `flow-csv-validator` agent to catch errors before upload.

### Create a test CSV with intentional errors

Create a CSV with common mistakes:

```csv
CI Name,CI,Namespace,Users,Enable_workshop_interface,Password,Activity,Purpose,Provisioning Date (UTC),Auto-stop (UTC),Auto-destroy (UTC)
Test Workshop,test.invalid.ci,user-test,999,True,pass123,Admin,QA,05/07/2026 14:00,05/07/2026 22:00,05/21/2026 14:00
```

This CSV has three errors:
- `test.invalid.ci` is not a valid catalog item
- `Users=999` likely exceeds catalog max
- Date format is MM/DD/YYYY instead of DD/MM/YYYY

### Run the validator

Ask Claude: "validate this CSV" and provide the CSV content.

Expected: Claude dispatches the `flow-csv-validator` agent, which checks every row against the spec and returns a structured report.

### Review the report

Walk through the output:
- ERROR entries: must be fixed before upload
- WARNING entries: may cause unexpected behavior
- Fix suggestions: concrete steps to resolve each issue

### Verification

The agent correctly identifies all three planted errors and suggests fixes.

---

## Step 4 — Workshop operations

**Goal:** Use the `flow-ops` skill to manage a deployed workshop.

### Extend auto-stop

Ask Claude: "extend the workshop stop time by 4 hours"

Expected: Claude uses the `flow-ops` skill, detects the "extend-stop" action, confirms the target, and executes.

Walk through:
- Operation preview before execution
- Confirmation prompt
- Result with success/failure status

### Verification

The operation completes successfully and the response confirms the extension.

---

## Step 5 — Pre-event readiness

**Goal:** Run the `flow-pre-event-checklist` agent for a go/no-go decision.

### Run the checklist

Ask Claude: "run a pre-event check" or "are we ready for the workshop?"

Expected: Claude dispatches the `flow-pre-event-checklist` agent, which runs all checks and produces a go/no-go verdict.

Walk through the checklist categories:
- **Infrastructure**: OCP cluster connectivity and token validity
- **Deployments**: all workshops deployed, no ghosts
- **QA Verification**: QA1 and QA2 passing
- **Capacity**: pool has sufficient ready instances
- **Timing**: auto-stop/destroy covers the event window

### Verification

The checklist runs all categories and produces a clear GO or NO-GO verdict with explanations.

---

## Verification

All five steps produce structured, actionable output:

| Step | Check |
|------|-------|
| 1 | Status dashboard shows deployments, QA, and pools |
| 2 | QA results have pass/fail with fix suggestions |
| 3 | CSV validator catches planted errors |
| 4 | Operations skill executes and confirms |
| 5 | Pre-event checklist produces go/no-go verdict |

---

## Challenge

Deploy a workshop from scratch using only the `flow-deploy` skill -- no manual CSV editing:

1. Invoke the `flow-deploy` skill: "deploy a workshop"
2. Follow the guided conversation to select a catalog item, set parameters, and generate the CSV
3. Let the skill validate and dry-run
4. If dry-run succeeds, deploy for real (or stop at dry-run if on a shared cluster)
5. Run QA using the `flow-qa` skill to verify the deployment

## Challenge Verification

- The `flow-deploy` skill guided you through the entire process
- CSV was generated, validated, and deployed (or dry-run'd) without manual editing
- QA results show the deployment status

---

## Completion

On module completion, write the progress marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/24.done
```
