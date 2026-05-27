
# Module 04 -- Deployment Intelligence

Estimated time: 20 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 01 recommended (RHDP-Flow MCP -- for context on the Flow ecosystem), Module 03 recommended (CSV Pipeline -- for context on offline CSV tools)

Install the rhdp-flow-intel MCP server for real-time deployment monitoring, ghost workshop detection, snapshot diffing, aggregate health dashboards, and pattern-based troubleshooting.

## Quick Setup (skip the walkthrough)

If you already understand MCP servers and just want the tools working:

```bash
# Auto-detect and install the package
PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-intel"
REPO_PATH="./rhdp-flow-intel"
if python3 -c "import rhdp_flow_intel" 2>/dev/null; then
  echo "PASS: rhdp-flow-intel already installed"
elif [ -d "$PLUGIN_PATH" ]; then
  pip install -e "$PLUGIN_PATH"
elif [ -d "$REPO_PATH" ]; then
  pip install -e "$REPO_PATH"
else
  echo "FAIL: rhdp-flow-intel not found. Install the courseware plugin first:"
  echo "  claude plugin add github:rhpds/claude-code-courseware"
fi
```

Then register globally in `~/.claude/settings.json`:

```bash
python3 << 'PYEOF'
import json, os, shutil
path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
settings.setdefault("mcpServers", {})
py = shutil.which("python3")
settings["mcpServers"]["rhdp-flow-intel"] = {
    "command": py,
    "args": ["-m", "rhdp_flow_intel"],
    "env": {"FLOW_API_URL": "http://localhost:8000"}
}
with open(path, "w") as f:
    json.dump(settings, f, indent=2)
print(f"PASS: rhdp-flow-intel registered globally (python3={py})")
PYEOF
```

Restart Claude Code and verify: ask Claude "show deployment status" -- it should call `flow_deployment_monitor`.

Skip to the [Challenge](#challenge) for hands-on practice.

## External Dependencies

This module uses the Two-Track Dependency Pattern. The `rhdp-flow-intel` package connects to the live Flow API, so results depend on backend availability.

- **rhdp-flow-intel package** -- a Python MCP server providing 5 deployment intelligence tools. Installed via `pip install -e` from a local checkout or plugin.
- **Python 3.10+** -- required runtime.
- **Flow API backend** -- the tools call the Flow API at `FLOW_API_URL` for live deployment data. Without it, the module runs as a conceptual walkthrough.
- **OpenShift cluster** -- the Flow API reads deployment state from the cluster. You do not need direct cluster access; the API handles it.

## Orientation

Print this once at the start:

```
You're setting up the rhdp-flow-intel MCP server, which gives Claude Code
5 tools for deployment intelligence. This takes about 20 minutes.

Module 03 covered the offline half -- CSV processing. This module covers
the live half -- monitoring deployments in real time, detecting ghost
workshops, comparing deployment snapshots, viewing aggregate health, and
troubleshooting failures using pattern matching. These tools connect to
the Flow API backend.

We'll cover:
  1. Install and configure the rhdp-flow-intel MCP server
  2. Monitor deployment status in real time
  3. Detect ghost workshops and generate cleanup commands
  4. Compare deployment snapshots to see what changed
  5. View aggregate health across deployments, QA, and pools
  6. Troubleshoot workshop failures using pattern matching

After this module you'll be able to get a complete picture of deployment
health and diagnose issues directly from Claude Code.

You'll need:
  - Claude Code installed and working (Module 01)
  - Python 3.10+
  - pip available
  - Flow API backend (for live data; conceptual track available without it)
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/26.started
```

## Preflight

Run these checks automatically. Show results as EXISTS/MISSING.

### Check 1: Python 3.10+ available

```bash
python3 -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null && echo "EXISTS: Python $(python3 --version 2>&1 | awk '{print $2}')" || echo "MISSING: Python 3.10+ required"
```

### Check 2: pip available

```bash
python3 -m pip --version >/dev/null 2>&1 && echo "EXISTS: pip $(python3 -m pip --version 2>&1 | awk '{print $2}')" || echo "MISSING: pip -- install with: python3 -m ensurepip"
```

### Check 3: rhdp-flow-intel package installed

```bash
if python3 -c "import rhdp_flow_intel" 2>/dev/null; then
  echo "EXISTS: rhdp-flow-intel package"
else
  echo "MISSING: rhdp-flow-intel package"
  echo ""
  echo "  Two options:"
  echo ""
  echo "  FULL EXPERIENCE (recommended):"
  PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-intel"
  REPO_PATH="./rhdp-flow-intel"
  if [ -d "$PLUGIN_PATH" ]; then
    echo "    pip install -e $PLUGIN_PATH"
  elif [ -d "$REPO_PATH" ]; then
    echo "    pip install -e $REPO_PATH"
  else
    echo "    claude plugin add github:rhpds/claude-code-courseware"
    echo "    pip install -e \$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-intel"
  fi
  echo "    Once installed, re-run this module."
  echo ""
  echo "  CONCEPTUAL OVERVIEW:"
  echo "    Continue without it. You'll learn what each tool does"
  echo "    but won't be able to run the tools hands-on."
fi
```

### Check 4: MCP server registered

```bash
FOUND=false
for f in "$HOME/.claude/settings.json" .claude/settings.json .claude/settings.local.json; do
  if [ -f "$f" ] && grep -q "rhdp-flow-intel" "$f" 2>/dev/null; then
    echo "EXISTS: rhdp-flow-intel MCP server registered in $f"
    FOUND=true
    break
  fi
done
if [ "$FOUND" = false ]; then
  echo "MISSING: rhdp-flow-intel MCP server not registered -- will configure in Step 1"
fi
```

### Check 5: Flow API reachable

```bash
if curl -sf http://localhost:8000/api/health --max-time 5 >/dev/null 2>&1; then
  echo "EXISTS: Flow API reachable at http://localhost:8000"
else
  echo "MISSING: Flow API not reachable"
  echo ""
  echo "  Two options:"
  echo ""
  echo "  FULL EXPERIENCE (recommended):"
  echo "    Start the Flow API backend (see Module 01 or the rhdp-flow docs)."
  echo "    Once running, re-run this module."
  echo ""
  echo "  CONCEPTUAL OVERVIEW:"
  echo "    Continue without it. You'll learn the tool concepts and"
  echo "    see sample output, but won't get live deployment data."
fi
```

Print summary: how many checks passed, what needs to be done.

If rhdp-flow-intel is MISSING or Flow API is not reachable, tell the user which track they are on:
- **Full experience**: install the package, start the API, and continue with hands-on steps
- **Conceptual overview**: skip hands-on steps, learn the concepts with sample output

---

## Step 1 -- Install and configure the MCP server

Skip if rhdp-flow-intel is already installed AND registered AND the Flow API is reachable.

**Goal:** Install the rhdp-flow-intel package and register it as an MCP server so Claude Code can call the 5 deployment intelligence tools.

### Install the package

```bash
PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-intel"
REPO_PATH="./rhdp-flow-intel"
if python3 -c "import rhdp_flow_intel" 2>/dev/null; then
  echo "PASS: rhdp-flow-intel already installed"
elif [ -d "$PLUGIN_PATH" ]; then
  pip install -e "$PLUGIN_PATH"
elif [ -d "$REPO_PATH" ]; then
  pip install -e "$REPO_PATH"
else
  echo "FAIL: rhdp-flow-intel not found. Install the courseware plugin first:"
  echo "  claude plugin add github:rhpds/claude-code-courseware"
fi
```

### Register the MCP server globally

```bash
python3 << 'PYEOF'
import json, os, shutil
path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
settings.setdefault("mcpServers", {})
py = shutil.which("python3")
settings["mcpServers"]["rhdp-flow-intel"] = {
    "command": py,
    "args": ["-m", "rhdp_flow_intel"],
    "env": {"FLOW_API_URL": "http://localhost:8000"}
}
with open(path, "w") as f:
    json.dump(settings, f, indent=2)
print(f"PASS: rhdp-flow-intel registered globally (python3={py})")
PYEOF
```

Update the `FLOW_API_URL` value if connecting to a different backend.

### Restart and verify

After adding the server, restart Claude Code. Then verify the tools are available.

The 5 tools you should see:

| Tool | Purpose |
|------|---------|
| `flow_deployment_monitor` | Real-time deployment status with progress tracking |
| `flow_ghost_detector` | Find ghost workshops and generate cleanup commands |
| `flow_deployment_diff` | Compare deployment snapshots to see what changed |
| `flow_event_dashboard` | Aggregate health report across deployments, QA, pools |
| `flow_troubleshoot` | Match symptoms to known failure patterns with fix suggestions |

### Verification

```bash
python3 -c "import rhdp_flow_intel; print('PASS: rhdp-flow-intel installed')" 2>/dev/null || echo "FAIL: rhdp-flow-intel not installed"
```

---

## Step 2 -- Monitor deployments

Skip if on the conceptual track. Skipped: requires rhdp-flow-intel and Flow API.

**Goal:** Use `flow_deployment_monitor` to see the current deployment state and understand the status categories.

### Run the monitor

Call `flow_deployment_monitor` with no arguments to get the current deployment overview.

### Understand the output

The monitor returns a structured report with each workshop's status. The key status categories are:

| Status | Meaning |
|--------|---------|
| READY | Workshop is provisioned and available for use |
| PROVISIONING | Workshop is currently being set up |
| ERROR | Provisioning failed -- needs investigation |
| `<none>` (ghost) | No phase set -- workshop is stuck (see Step 3) |

The report also includes:
- **Provisioning progress**: percentage complete for workshops still deploying
- **Time in state**: how long each workshop has been in its current status
- **Flagged issues**: workshops that have been in PROVISIONING too long or have errors

### What to look for

- Workshops stuck in PROVISIONING for more than 30 minutes usually indicate a problem
- ERROR status includes the error message from the provisioner
- A high ratio of `<none>` workshops suggests a catalog or namespace issue

### Verification

The monitor returns a deployment report with at least status and workshop name for each entry. If the Flow API is running with test data, you should see at least one workshop listed.

---

## Step 3 -- Detect ghost workshops

Skip if on the conceptual track. Skipped: requires rhdp-flow-intel and Flow API.

**Goal:** Use `flow_ghost_detector` to find ghost workshops and understand why they happen.

### What are ghost workshops?

Ghost workshops are deployments stuck in `PHASE: <none>` -- they have a Workshop custom resource on the cluster but no corresponding provisioned environment. They consume cluster resources without providing a usable workshop.

Common causes:
- **CatalogItem not found**: the CI reference in the CSV does not match any catalog item in the target namespace
- **Provisioner fails silently**: the provisioner starts but exits without setting a phase
- **Namespace mismatch**: the workshop was created in a namespace where the provisioner has no permissions
- **Stale entries**: workshops from a previous event that were never cleaned up

### Run the detector

Call `flow_ghost_detector` with no arguments to scan for ghost workshops.

### Review the output

The detector returns:
- **ghost_count**: total number of ghost workshops found
- **ghosts**: list of ghost workshops with their name, namespace, creation time, and suspected cause
- **cleanup_commands**: ready-to-run `oc delete` commands for each ghost workshop
- **summary**: overall assessment and recommendations

### Cleanup workflow

The cleanup commands are provided for review -- they are not executed automatically. The typical workflow:

1. Run `flow_ghost_detector` to identify ghosts
2. Review the suspected causes -- some ghosts may be intentional (e.g., workshops being debugged)
3. Copy the cleanup commands for confirmed ghosts
4. Run the cleanup commands manually or through the ops pipeline

### Verification

The detector returns a report with ghost count. If there are ghosts, each entry includes a cleanup command. If there are no ghosts, the report says so explicitly.

---

## Step 4 -- Compare deployment snapshots

Skip if on the conceptual track. Skipped: requires rhdp-flow-intel and Flow API.

**Goal:** Use `flow_deployment_diff` to compare two points in time and see what changed in the deployment state.

### How snapshot diffing works

The deployment diff tool compares two snapshots of the deployment state. This is useful for:
- Verifying that a deployment wave completed as expected
- Tracking what changed during an incident
- Confirming cleanup commands removed the right workshops

### Take a baseline

First, call `flow_deployment_monitor` to get the current state. This is your baseline.

### Make a change (or wait)

If you are working in a live environment, wait for a deployment change or trigger one (e.g., deploy a test workshop). In a test environment, you can modify the test data.

### Run the diff

Call `flow_deployment_diff` with:
- `baseline`: the deployment data from the first monitor call
- `current`: results from a new monitor call (or leave empty to fetch current state)

### Review the output

The diff returns a structured comparison:
- **added**: workshops present now but not in the baseline
- **removed**: workshops in the baseline but not present now
- **changed**: workshops present in both but with status or field changes
- **unchanged**: count of workshops with no changes

Each changed entry shows the specific fields that differ and their before/after values.

### Verification

The diff returns a structured report. If no changes occurred, the added/removed/changed lists are empty and unchanged shows the total count.

---

## Step 5 -- Event dashboard

Skip if on the conceptual track. Skipped: requires rhdp-flow-intel and Flow API.

**Goal:** Use `flow_event_dashboard` for an aggregate health view combining deployment status, QA results, and pool availability.

### Run the dashboard

Call `flow_event_dashboard` with no arguments for the overall view. Optionally pass an event name to scope the dashboard to a specific event.

### Understand the output

The dashboard aggregates data from three sources:

**Deployment status breakdown:**
- Count of workshops by status (READY, PROVISIONING, ERROR, ghost)
- Percentage ready vs total

**QA results summary:**
- Pass/fail counts from recent QA runs
- Workshops that have never been QA-tested
- Common failure reasons

**Pool availability:**
- Available capacity by pool
- Pools at or near exhaustion
- Estimated time to provision based on current queue

**Overall health indicator:**
- GREEN: all workshops READY, QA passing, pools have capacity
- YELLOW: some issues but no outages -- e.g., QA failures, low pool capacity
- RED: outages or critical issues -- e.g., high error rate, pools exhausted

### When to use the dashboard

- **Before an event**: confirm all workshops are READY and QA is green
- **During an event**: monitor for emerging issues
- **After an event**: review the final state for post-mortem

### Verification

The dashboard returns a structured health report with at least the deployment status breakdown and overall health indicator.

---

## Step 6 -- Troubleshoot a workshop

Skip if on the conceptual track. Skipped: requires rhdp-flow-intel and Flow API.

**Goal:** Use `flow_troubleshoot` to diagnose workshop issues using pattern matching against known failure modes.

### How troubleshooting works

The troubleshoot tool takes a workshop name or set of symptoms and matches them against a library of known failure patterns. Each pattern has:
- **Symptoms**: what the failure looks like (error messages, status patterns)
- **Root cause**: what actually went wrong
- **Confidence**: how closely the symptoms match (high, medium, low)
- **Fix steps**: recommended actions to resolve the issue

### Troubleshoot a ghost workshop

If Step 3 found ghost workshops, pick one and run:

Call `flow_troubleshoot` with:
- `workshop_name`: the name of a ghost workshop from the detector output

### Review the output

The troubleshooter returns:
- **matched_patterns**: list of patterns that match the symptoms, ranked by confidence
- **top_match**: the highest-confidence pattern with full details
- **fix_steps**: ordered list of actions to resolve the issue
- **related_issues**: other workshops that may be affected by the same root cause

### Troubleshoot a permission error

For a second example, try troubleshooting with symptoms instead of a workshop name:

Call `flow_troubleshoot` with:
- `symptoms`: `"forbidden: cannot create resource workshops in namespace babylon-catalog-event"`

The troubleshooter should match this to a permissions/RBAC pattern and suggest:
- Checking the service account permissions
- Verifying the namespace exists and has the correct labels
- Reviewing the RBAC bindings for the provisioner

### Common failure patterns

The troubleshooter recognizes these categories:
- **Ghost workshop**: no phase set, CatalogItem missing
- **Permission denied**: RBAC issues, namespace restrictions
- **Timeout**: provisioning exceeded time limit
- **Resource exhaustion**: cluster capacity, pool limits
- **Catalog mismatch**: CI name does not match any available CatalogItem

### Verification

The troubleshooter returns at least one matched pattern with confidence level and fix steps. If no patterns match, it says so and suggests manual investigation.

---

## Verification

Run all preflight checks again as PASS/FAIL:

```bash
PASS=0
TOTAL=5

python3 -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null && { echo "PASS: Python 3.10+"; PASS=$((PASS+1)); } || echo "FAIL: Python 3.10+"
python3 -m pip --version >/dev/null 2>&1 && { echo "PASS: pip available"; PASS=$((PASS+1)); } || echo "FAIL: pip"
python3 -c "import rhdp_flow_intel" 2>/dev/null && { echo "PASS: rhdp-flow-intel installed"; PASS=$((PASS+1)); } || echo "FAIL: rhdp-flow-intel not installed"

MCP_FOUND=false
for f in "$HOME/.claude/settings.json" .claude/settings.json .claude/settings.local.json; do
  if [ -f "$f" ] && grep -q "rhdp-flow-intel" "$f" 2>/dev/null; then
    echo "PASS: MCP server registered in $f"; PASS=$((PASS+1))
    MCP_FOUND=true
    break
  fi
done
if [ "$MCP_FOUND" = false ]; then
  echo "FAIL: MCP server not registered"
fi

curl -sf http://localhost:8000/api/health --max-time 5 >/dev/null 2>&1 && { echo "PASS: Flow API reachable"; PASS=$((PASS+1)); } || echo "FAIL: Flow API not reachable"

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:

```
All checks passed. The rhdp-flow-intel MCP server is installed and configured.
You can now monitor deployments, detect ghosts, diff snapshots, view health
dashboards, and troubleshoot failures directly from Claude Code.
```

If any fail, tell the user which step to re-run.

---

## Challenge

```
Run a full health audit of the current deployment state:

1. Get the deployment monitor report (flow_deployment_monitor)
2. Check for ghost workshops (flow_ghost_detector)
3. Run the event dashboard (flow_event_dashboard)
4. Pick one workshop that has issues and troubleshoot it (flow_troubleshoot)

Tell me:
  1. How many workshops are READY vs total?
  2. Are there any ghost workshops? If so, how many?
  3. What is the overall event health (GREEN/YELLOW/RED)?
  4. What pattern did the troubleshooter match for the problematic
     workshop, and what fix does it suggest?
```

## Challenge Verification

Check the user's answers:

1. **READY vs total**: Verify the counts match the deployment monitor output. The user should report something like "X out of Y workshops are READY."

2. **Ghost workshops**: Verify against the ghost detector output. If there are ghosts, the user should report the count. If none, they should say so.

3. **Overall health**: Verify against the event dashboard output. The user should report GREEN, YELLOW, or RED with a brief explanation of why.

4. **Troubleshooter pattern**: Verify the user identified a matched pattern by name or description, reported the confidence level, and described the recommended fix. The specific pattern depends on the live data.

If the user is on the conceptual track (no Flow API), accept answers based on the sample output discussed in the walkthrough steps.

If the user's answers are correct, write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/26.done
```

Then print:

```
Module 04 complete.

You can now run deployment intelligence from Claude Code:
  - Monitor deployment status in real time
  - Detect and clean up ghost workshops
  - Compare deployment snapshots before and after changes
  - View aggregate health across an entire event
  - Troubleshoot failures with pattern-matched fix suggestions

Next module: /learn-flow-05-workshop-intake

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
