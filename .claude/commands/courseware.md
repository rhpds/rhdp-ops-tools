# RHDP Ops Tools

Before displaying the catalog, run the progress scan.

## Progress Scan

Run this silently to detect completion/in-progress state:

```bash
PROGRESS_DIR="$HOME/.claude/courseware-progress"
mkdir -p "$PROGRESS_DIR"

declare -A MODULE_STATUS

for i in {1..5}; do
  NUM=$(printf "%02d" $i)
  DONE_FILE="$PROGRESS_DIR/flow-$NUM.done"
  STARTED_FILE="$PROGRESS_DIR/flow-$NUM.started"
  
  if [[ -f "$DONE_FILE" ]]; then
    MODULE_STATUS["flow-$NUM"]="DONE"
  elif [[ -f "$STARTED_FILE" ]]; then
    MODULE_STATUS["flow-$NUM"]="IN PROGRESS"
  else
    MODULE_STATUS["flow-$NUM"]=""
  fi
done

export MODULE_STATUS
```

After running the scan, display the catalog with status indicators:

---

## RHDP Ops Tools Courseware

### Flow -- Workshop Automation

| # | Module | Time | Status |
|---|--------|------|--------|
| `01` | RHDP-Flow MCP | 20 min | ${MODULE_STATUS["flow-01"]} |
| `02` | RHDP-Flow Ops | 15 min | ${MODULE_STATUS["flow-02"]} |
| `03` | CSV Pipeline | 20 min | ${MODULE_STATUS["flow-03"]} |
| `04` | Deployment Intelligence | 20 min | ${MODULE_STATUS["flow-04"]} |
| `05` | Event-Scale Operations | 30 min | ${MODULE_STATUS["flow-05"]} |

**Total: 105 minutes**

### Intake -- Workshop Intake (coming soon)

| # | Module | Time |
|---|--------|------|
| `01` | Workshop Intake | 15 min |

---

## Getting Started

**Plugin install** (recommended):
```bash
claude plugin add github:rhpds/rhdp-ops-tools
```

**Prerequisites check**:
```
/preflight
```

**Start a module**:
```
/learn-flow-01
```

---

## Module Routing Table

When the user provides a module number, route to the corresponding command:

| Input | Command |
|-------|---------|
| `01`, `flow-01`, `flow 01` | `/learn-flow-01-rhdp-flow-mcp` |
| `02`, `flow-02`, `flow 02` | `/learn-flow-02-rhdp-flow-ops` |
| `03`, `flow-03`, `flow 03` | `/learn-flow-03-csv-pipeline` |
| `04`, `flow-04`, `flow 04` | `/learn-flow-04-deployment-intel` |
| `05`, `flow-05`, `flow 05` | `/learn-flow-05-event-scale-ops` |

---

**Module count**: 5 Flow modules available, 1 Intake module planned.

For installation help, see the README at https://github.com/rhpds/rhdp-ops-tools
