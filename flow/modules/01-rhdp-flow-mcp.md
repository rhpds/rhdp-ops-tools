
# Module 01 — RHDP-Flow MCP

Estimated time: 20 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 11 recommended (Building MCP Servers -- for context on how MCP servers work)

Install and use the RHDP-Flow MCP server to manage OpenShift workshop deployments through 15 structured tools.

## Quick Setup (skip the walkthrough)

If you already understand MCP servers and just want the tools working:

```bash
# 1. Clone or update the source repo
REPO_DIR="$HOME/repos/rhpds-utils"
if [ ! -d "$REPO_DIR" ]; then
  git clone git@github.com:rhpds/rhpds-utils.git "$REPO_DIR"
else
  cd "$REPO_DIR" && git pull origin main
fi

# 2. Log in to the target OCP cluster
oc login --token=sha256~<your-token> --server=https://api.ocp-us-east-1.infra.open.redhat.com:6443

# 3. Auto-detect and install the package
PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-mcp"
REPO_PATH="./rhdp-flow-mcp"
if python3 -c "import rhdp_flow_mcp" 2>/dev/null; then
  echo "PASS: rhdp-flow-mcp already installed"
elif [ -d "$PLUGIN_PATH" ]; then
  pip install -e "$PLUGIN_PATH"
elif [ -d "$REPO_PATH" ]; then
  pip install -e "$REPO_PATH"
else
  echo "FAIL: rhdp-flow-mcp not found. Install the courseware plugin first:"
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
settings["mcpServers"]["rhdp-flow"] = {
    "command": py,
    "args": ["-m", "rhdp_flow_mcp"],
    "env": {"FLOW_API_URL": "https://rhdp-flow.apps.ocp-us-east-1.infra.open.redhat.com"}
}
with open(path, "w") as f:
    json.dump(settings, f, indent=2)
print(f"PASS: rhdp-flow registered globally (python3={py})")
PYEOF
```

Restart Claude Code and verify: ask Claude "check flow health" -- it should call `flow_health`.

Skip to the [Challenge](#challenge) for hands-on practice.

## External Dependencies

This module depends on services outside your local environment:

- **RHDP-Scheduler repo** -- the Flow tool source lives in `rhpds/rhpds-utils` under `RHDP-Scheduler/`. You need a local clone, kept up to date with `main`.
- **Flow API on OCP** -- the MCP server wraps the RHDP-Flow REST API, which runs as a service on an OCP cluster. You need the cluster's Flow route URL.
- **OCP authentication** -- you must be logged in with `oc login` using your personal ephemeral token. The token is short-lived and cluster-specific. Run `oc whoami` to confirm.
- **PyPI** -- `mcp[cli]`, `httpx`, and `pydantic` packages.

## Orientation

Print this once at the start:

```
You're setting up the RHDP-Flow MCP server, which gives Claude Code 15 tools
for workshop deployment automation. This takes about 20 minutes.

RHDP-Flow is the team's workshop automation system. It deploys OpenShift
workshops from CSV schedules, manages operations (lock, extend, scale),
runs QA checks, and handles resource pools. The MCP server wraps all of
this into structured tools that Claude Code can call directly.

We'll cover:
  1. Configure the MCP server and connect to the Flow backend
  2. Explore the catalog of available workshops
  3. Check resource pool availability
  4. Generate a deployment CSV from structured input
  5. Validate and dry-run a deployment

After this module you'll be able to manage workshops through Claude Code
instead of the Flow UI or CLI.

You'll need:
  - Claude Code installed and working (Module 01)
  - Local clone of rhpds/rhpds-utils (contains RHDP-Scheduler source)
  - oc CLI logged in to the target OCP cluster (personal ephemeral token)
  - The cluster's Flow route URL
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/23.started
```

## Preflight

Run these checks automatically. Show results as EXISTS/MISSING.

### Check 1: Claude Code installed

```bash
which claude >/dev/null 2>&1 && echo "EXISTS: Claude Code CLI" || echo "MISSING: Claude Code CLI -- complete Module 01 first"
```

### Check 2: Python 3.10+ available

```bash
python3 -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null && echo "EXISTS: Python 3.10+" || echo "MISSING: Python 3.10+ required"
```

### Check 3: RHDP-Scheduler repo cloned and current

```bash
REPO_DIR="$HOME/repos/rhpds-utils"
if [ ! -d "$REPO_DIR/RHDP-Scheduler" ]; then
  echo "MISSING: rhpds-utils repo not found at $REPO_DIR -- will clone in Step 1"
else
  cd "$REPO_DIR"
  git fetch origin main --quiet 2>/dev/null
  LOCAL=$(git rev-parse HEAD 2>/dev/null)
  REMOTE=$(git rev-parse origin/main 2>/dev/null)
  if [ "$LOCAL" = "$REMOTE" ]; then
    echo "EXISTS: RHDP-Scheduler repo up to date ($(git log -1 --format='%h %s' 2>/dev/null))"
  else
    echo "EXISTS: RHDP-Scheduler repo found but behind origin/main -- will update in Step 1"
  fi
fi
```

### Check 4: oc CLI configured

```bash
oc whoami >/dev/null 2>&1 && echo "EXISTS: oc CLI authenticated as $(oc whoami)" || echo "MISSING: oc CLI not authenticated -- run 'oc login' first"
```

### Check 5: rhdp-flow-mcp installed

```bash
python3 -c "import rhdp_flow_mcp" 2>/dev/null && echo "EXISTS: rhdp-flow-mcp package" || echo "MISSING: rhdp-flow-mcp package -- will install in Step 1"
```

### Check 6: MCP server registered

```bash
FOUND=false
for f in "$HOME/.claude/settings.json" .claude/settings.json .claude/settings.local.json; do
  if [ -f "$f" ] && grep -q "rhdp-flow" "$f" 2>/dev/null; then
    echo "EXISTS: rhdp-flow MCP server registered in $f"
    FOUND=true
    break
  fi
done
if [ "$FOUND" = false ]; then
  echo "MISSING: rhdp-flow MCP server not registered -- will configure in Step 1"
fi
```

Print summary: how many checks passed, what needs to be done.

---

## Step 1 — Configure the MCP server

**Goal:** Clone or update the RHDP-Scheduler source, install the rhdp-flow-mcp package, and register it with Claude Code.

### Clone or update the RHDP-Scheduler repo

The Flow tool source lives in the `rhpds/rhpds-utils` monorepo under `RHDP-Scheduler/`. Clone it if you don't have it, or pull the latest if you do.

Replace `<your-github-id>` with your `rhpds` org GitHub username (e.g., `rhjcd`):

```bash
REPO_DIR="$HOME/repos/rhpds-utils"
GH_USER="<your-github-id>"

if [ ! -d "$REPO_DIR" ]; then
  echo "Cloning rhpds-utils..."
  git clone "git@github.com:rhpds/rhpds-utils.git" "$REPO_DIR"
else
  echo "Updating rhpds-utils to latest main..."
  cd "$REPO_DIR" && git pull origin main
fi

# Verify the RHDP-Scheduler directory exists
ls "$REPO_DIR/RHDP-Scheduler/" >/dev/null 2>&1 && echo "PASS: RHDP-Scheduler found" || echo "FAIL: RHDP-Scheduler directory missing"
```

### Install the package

```bash
PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-mcp"
REPO_PATH="./rhdp-flow-mcp"
if python3 -c "import rhdp_flow_mcp" 2>/dev/null; then
  echo "PASS: rhdp-flow-mcp already installed"
elif [ -d "$PLUGIN_PATH" ]; then
  pip install -e "$PLUGIN_PATH"
elif [ -d "$REPO_PATH" ]; then
  pip install -e "$REPO_PATH"
else
  echo "FAIL: rhdp-flow-mcp not found. Install the courseware plugin first:"
  echo "  claude plugin add github:rhpds/claude-code-courseware"
fi
```

### Authenticate to the target OCP cluster

Log in with your personal ephemeral token. Get a token from the cluster's OAuth page or from your team lead:

```bash
oc login --token=sha256~<your-token> --server=https://api.<cluster-domain>:6443
```

For the production cluster:

```bash
oc login --token=sha256~<your-token> --server=https://api.ocp-us-east-1.infra.open.redhat.com:6443
```

Verify authentication:

```bash
oc whoami && echo "PASS: authenticated" || echo "FAIL: not logged in"
```

Tokens are ephemeral -- if you get a 401 error later, re-run `oc login` with a fresh token.

### Determine the Flow API URL

The Flow API runs as a service on the OCP cluster. Ask the user for their cluster's Flow route:

| Cluster | Flow Route URL |
|---------|---------------|
| Production (us-east-1) | `https://rhdp-flow.apps.ocp-us-east-1.infra.open.redhat.com` |
| Other clusters | `https://rhdp-flow.apps.<cluster-domain>` |
| Local dev server | `http://localhost:8000` (development only) |

### Register the MCP server globally

```bash
python3 << 'PYEOF'
import json, os, shutil
path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
settings.setdefault("mcpServers", {})
py = shutil.which("python3")
settings["mcpServers"]["rhdp-flow"] = {
    "command": py,
    "args": ["-m", "rhdp_flow_mcp"],
    "env": {"FLOW_API_URL": "https://rhdp-flow.apps.ocp-us-east-1.infra.open.redhat.com"}
}
with open(path, "w") as f:
    json.dump(settings, f, indent=2)
print(f"PASS: rhdp-flow registered globally (python3={py})")
PYEOF
```

Update the `FLOW_API_URL` value if connecting to a different cluster (see table above).

### Verification

Ask Claude: "check flow health"

Expected: Claude calls `flow_health` and returns backend status including cluster URL, user identity, and connection status.

```
{
  "status": "ok",
  "oc_connected": true,
  "cluster_url": "https://api.ocp-us-east-1.infra.open.redhat.com:6443",
  "user": "<your-username>",
  "message": "Connected to cluster"
}
```

If status is "error", check:
- Is `FLOW_API_URL` set correctly? (must be the cluster's Flow route)
- Are you logged in? Run `oc whoami` -- if it fails, re-run `oc login` with a fresh token
- Can you reach the Flow route? (`curl -sf $FLOW_API_URL/api/health`)

---

## Step 2 — Explore the catalog

**Goal:** Browse available workshop catalog items and understand their parameters.

### List catalog items

Ask Claude: "list available catalog items"

Expected: Claude calls `flow_catalog_items` and returns the full catalog.

Walk through the output with the user:
- **id**: the catalog item identifier (e.g., `openshift-cnv.ocp-virt-roadshow-multi-user.prod`)
- **description**: what the workshop teaches
- **max_users**: maximum users per deployment (exceeding this causes validation errors)
- **parameters**: configurable settings for the workshop

### Verification

User can identify at least one catalog item ID, its max user limit, and describe what it does.

---

## Step 3 — Check resource pools

**Goal:** Understand pool availability before deploying.

### List all pools

Ask Claude: "show me the resource pools"

Expected: Claude calls `flow_pools` and returns pool status.

Explain the fields:
- **ready**: instances available for immediate claim
- **claimed**: instances currently in use
- **provisioning**: instances being set up

### Look up a specific pool

Ask Claude: "check the pool for `<catalog_item_id>`" (use one from Step 2)

Expected: Claude calls `flow_pool_lookup` with the catalog item.

### Verification

User can read pool status and knows whether instances are available for their chosen catalog item.

---

## Step 4 — Generate a deployment CSV

**Goal:** Create a valid Flow CSV from structured input without manual editing.

### Build the input

Help the user construct a JSON input for a single workshop:

```json
{
  "workshops": [
    {
      "ci": "<catalog_item_from_step_2>",
      "namespace": "user-<username>",
      "users": 10
    }
  ],
  "start_time": "2026-05-07T14:00:00",
  "auto_stop_hours": 8,
  "auto_destroy_days": 14,
  "password": "workshop123"
}
```

### Generate the CSV

Ask Claude: "generate a flow CSV with this input: <json>"

Expected: Claude calls `flow_generate_csv` and returns a valid CSV string.

Walk through the output:
- Date format is DD/MM/YYYY HH:MM (not US format)
- Auto-stop is calculated from start_time + auto_stop_hours
- Auto-destroy is calculated from start_time + auto_destroy_days
- CI Name defaults to the CI value

### Verification

The generated CSV has the correct columns, date format, and calculated stop/destroy times.

---

## Step 5 — Validate and dry-run

**Goal:** Upload the CSV, validate it against catalog rules, and preview the deployment.

### Upload

Ask Claude: "upload this CSV to Flow" and provide the CSV from Step 4.

Expected: Claude calls `flow_upload_csv` and returns the upload result with row count.

### Validate

Ask Claude: "validate the uploaded schedules"

Expected: Claude calls `flow_validate` with check="all" and returns validation results.

If validation finds issues:
- **num_users**: a row exceeds the catalog item's max_users
- **catalog_namespaces**: a namespace doesn't match the expected pattern

### Dry-run

Ask Claude: "do a dry-run deployment"

Expected: Claude calls `flow_deploy` with dry_run=true and returns the manifests that would be applied.

Review the dry-run output: resource names, namespaces, labels.

### Verification

Upload succeeded, validation passed (or user understands the violations), and dry-run shows the expected manifests.

---

## Verification

All five steps produce expected output:

| Step | Check |
|------|-------|
| 1 | `flow_health` returns status "ok" |
| 2 | Can list and describe catalog items |
| 3 | Can read pool availability |
| 4 | CSV generates with correct format and calculations |
| 5 | Upload, validate, and dry-run all succeed |

---

## Challenge

Generate a staggered bulk deployment CSV for a real catalog item on the team cluster:

1. Pick a catalog item from the team's catalog
2. Create a bulk deployment with:
   - 5 workshop instances
   - 10-minute staggered intervals
   - 20 users per instance
   - 8-hour auto-stop, 14-day auto-destroy
3. Generate the CSV using `flow_generate_csv`
4. Validate the CSV using `flow_validate`
5. Dry-run the deployment using `flow_deploy` with dry_run=true

## Challenge Verification

- The generated CSV has 5 rows
- Provisioning dates are staggered by 10 minutes (e.g., 10:00, 10:10, 10:20, 10:30, 10:40)
- Validation passes with no errors
- Dry-run succeeds and shows 5 sets of manifests

---

## Completion

On module completion, write the progress marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/23.done
```
