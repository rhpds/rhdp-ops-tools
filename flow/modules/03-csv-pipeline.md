
# Module 03 -- CSV Pipeline

Estimated time: 20 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 11 recommended (Building MCP Servers -- for context on how MCP servers work)

Install the rhdp-flow-csv MCP server and process workshop CSVs through the full pipeline -- transform, fix, expand, update, and diff.

## Quick Setup (skip the walkthrough)

If you already understand MCP servers and just want the tools working:

```bash
# Auto-detect and install the package
PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-csv"
REPO_PATH="./rhdp-flow-csv"
if python3 -c "import rhdp_flow_csv" 2>/dev/null; then
  echo "PASS: rhdp-flow-csv already installed"
elif [ -d "$PLUGIN_PATH" ]; then
  pip install -e "$PLUGIN_PATH"
elif [ -d "$REPO_PATH" ]; then
  pip install -e "$REPO_PATH"
else
  echo "FAIL: rhdp-flow-csv not found. Install the courseware plugin first:"
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
settings["mcpServers"]["rhdp-flow-csv"] = {
    "command": py,
    "args": ["-m", "rhdp_flow_csv"]
}
with open(path, "w") as f:
    json.dump(settings, f, indent=2)
print(f"PASS: rhdp-flow-csv registered globally (python3={py})")
PYEOF
```

Restart Claude Code and verify: ask Claude "fix this CSV" with a sample -- it should call `flow_fix_csv`.

Skip to the [Challenge](#challenge) for hands-on practice.

## External Dependencies

This module uses the Two-Track Dependency Pattern. The `rhdp-flow-csv` package is a separate Python package that may or may not be installed in your environment.

- **rhdp-flow-csv package** -- a Python MCP server providing 5 CSV tools. Installed via `pip install -e` from a local checkout or plugin.
- **Python 3.10+** -- required runtime.
- **No API or cluster access needed** -- unlike Module 01, this module works entirely offline with local CSV files.

## Orientation

Print this once at the start:

```
You're setting up the rhdp-flow-csv MCP server, which gives Claude Code
5 tools for processing workshop CSV schedules. This takes about 20 minutes.

The CSV pipeline is the offline half of workshop deployment. It takes messy
planning spreadsheets and turns them into Flow-compliant CSVs -- no API
or cluster access needed.

We'll cover:
  1. Install and configure the rhdp-flow-csv MCP server
  2. Transform a messy runbook into Flow-compliant CSV
  3. Fix common CSV issues (dates, missing columns)
  4. Expand multi-asset workshop rows
  5. Bulk-update parameters across rows
  6. Diff two CSV schedules

After this module you'll be able to clean up any workshop CSV
using Claude Code instead of manual spreadsheet editing.

You'll need:
  - Claude Code installed and working (Module 01)
  - Python 3.10+
  - pip available
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/25.started
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

### Check 3: rhdp-flow-csv package installed

```bash
if python3 -c "import rhdp_flow_csv" 2>/dev/null; then
  echo "EXISTS: rhdp-flow-csv package"
else
  echo "MISSING: rhdp-flow-csv package"
  echo ""
  echo "  Two options:"
  echo ""
  echo "  FULL EXPERIENCE (recommended):"
  PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-csv"
  REPO_PATH="./rhdp-flow-csv"
  if [ -d "$PLUGIN_PATH" ]; then
    echo "    pip install -e $PLUGIN_PATH"
  elif [ -d "$REPO_PATH" ]; then
    echo "    pip install -e $REPO_PATH"
  else
    echo "    claude plugin add github:rhpds/claude-code-courseware"
    echo "    pip install -e \$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-csv"
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
  if [ -f "$f" ] && grep -q "rhdp-flow-csv" "$f" 2>/dev/null; then
    echo "EXISTS: rhdp-flow-csv MCP server registered in $f"
    FOUND=true
    break
  fi
done
if [ "$FOUND" = false ]; then
  echo "MISSING: rhdp-flow-csv MCP server not registered -- will configure in Step 1"
fi
```

Print summary: how many checks passed, what needs to be done.

If rhdp-flow-csv is MISSING, tell the user which track they are on:
- **Full experience**: install the package and continue with hands-on steps
- **Conceptual overview**: skip hands-on steps, learn the concepts

---

## Step 1 -- Install and configure the MCP server

Skip if rhdp-flow-csv is already installed AND registered.

**Goal:** Install the rhdp-flow-csv package and register it as an MCP server so Claude Code can call the 5 CSV tools.

### Install the package

```bash
PLUGIN_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-csv"
REPO_PATH="./rhdp-flow-csv"
if python3 -c "import rhdp_flow_csv" 2>/dev/null; then
  echo "PASS: rhdp-flow-csv already installed"
elif [ -d "$PLUGIN_PATH" ]; then
  pip install -e "$PLUGIN_PATH"
elif [ -d "$REPO_PATH" ]; then
  pip install -e "$REPO_PATH"
else
  echo "FAIL: rhdp-flow-csv not found. Install the courseware plugin first:"
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
settings["mcpServers"]["rhdp-flow-csv"] = {
    "command": py,
    "args": ["-m", "rhdp_flow_csv"]
}
with open(path, "w") as f:
    json.dump(settings, f, indent=2)
print(f"PASS: rhdp-flow-csv registered globally (python3={py})")
PYEOF
```

### Restart and verify

After adding the server, restart Claude Code. Then verify the tools are available.

The 5 tools you should see:

| Tool | Purpose |
|------|---------|
| `flow_transform_runbook` | Convert messy planning spreadsheets to Flow-compliant CSV |
| `flow_fix_csv` | Validate and auto-fix common CSV issues |
| `flow_expand_multi_asset` | Detect and expand multi-asset workshop rows |
| `flow_bulk_parameter_update` | Apply parameter changes to matching rows |
| `flow_csv_diff` | Compare two CSV schedules |

### Verification

```bash
python3 -c "import rhdp_flow_csv; print('PASS: rhdp-flow-csv installed')" 2>/dev/null || echo "FAIL: rhdp-flow-csv not installed"
```

---

## Step 2 -- Transform a runbook

Skip if on the conceptual track. Skipped: requires rhdp-flow-csv.

**Goal:** Take a messy planning spreadsheet and convert it into a Flow-compliant CSV using `flow_transform_runbook`.

### Create a sample messy CSV

Write this to `/tmp/messy-runbook.csv`:

```csv
Lab Code,Title,Session Date,Session Start,Attendees,Namespace,CI
LB1234,Image Mode Workshop,2026-06-15,09:00:00,25,user-jsmith-redhat-com,summit-2026.lb1234-image-mode
LB5678,OpenShift Virtualization,2026-06-15,13:00:00,30,user-jdoe-redhat-com,summit-2026.lb5678-ocp-virt
LB9012,Ansible Automation,2026-06-16,10:00:00,20,user-asmith-redhat-com,summit-2026.lb9012-ansible
```

This CSV has non-standard column names, separate date and time columns, and no auto-stop or auto-destroy fields. The transform tool will fix all of this.

### Run the transform

Call `flow_transform_runbook` with:
- `csv_content`: the contents of `/tmp/messy-runbook.csv`
- `event_config`: `{"timezone": "UTC", "target_timezone": "UTC", "catalog_namespace": "babylon-catalog-event", "naming_template": "Day 1-Test-{title}"}`

### Review the output

The tool should produce a Flow-compliant CSV with:
- Standard column names (`CI Name`, `CI`, `Namespace`, `Users`, `Provisioning Date (UTC)`, `Auto-stop (UTC)`, `Auto-destroy (UTC)`)
- Combined date/time in DD/MM/YYYY HH:MM format
- Calculated auto-stop and auto-destroy fields
- CI Name derived from the naming template

Walk through the auto-fixes applied:
- Column renaming: `Lab Code` is dropped, `Title` maps to naming, `Session Date` + `Session Start` merge into `Provisioning Date (UTC)`
- `Attendees` becomes `Users`
- Missing fields are generated with sensible defaults

### Verification

The output CSV has all required Flow columns and 3 data rows. Date format is DD/MM/YYYY HH:MM.

---

## Step 3 -- Fix CSV issues

Skip if on the conceptual track. Skipped: requires rhdp-flow-csv.

**Goal:** Use `flow_fix_csv` to validate a CSV and auto-fix common issues.

### Create a CSV with problems

Write this to `/tmp/broken-schedule.csv`:

```csv
CI Name,CI,Namespace,Users,Provisioning Date (UTC),Auto-stop (UTC),Auto-destroy (UTC)
Test Workshop,summit.test-workshop,user-test,15,06/15/2026 09:00,06/15/2026 17:00,06/29/2026 09:00
Another Lab,summit.another-lab,user-demo,20,2026-06-16 10:00,2026-06-16 18:00,2026-06-30 10:00
```

This CSV has two problems:
- Row 1: US date format (MM/DD/YYYY) instead of DD/MM/YYYY
- Row 2: ISO date format (YYYY-MM-DD) instead of DD/MM/YYYY

### Run the fixer

Call `flow_fix_csv` with:
- `csv_content`: the contents of `/tmp/broken-schedule.csv`

### Review the output

The tool returns:
- **fixed_csv**: the corrected CSV content
- **fixes_applied**: a list of every auto-fix with row number and description
- **warnings**: any issues that could not be auto-fixed

Walk through the fixes:
- Date format corrections: US and ISO dates converted to DD/MM/YYYY HH:MM
- Any missing optional columns added with defaults

### Verification

The fixed CSV has dates in DD/MM/YYYY HH:MM format for all rows. The fixes_applied list describes each change.

---

## Step 4 -- Expand multi-asset workshops

Skip if on the conceptual track. Skipped: requires rhdp-flow-csv.

**Goal:** Detect and expand rows where multiple catalog items are packed into a single CI field.

### Create a CSV with multi-asset rows

Write this to `/tmp/multi-asset.csv`:

```csv
CI Name,CI,Namespace,Users,Provisioning Date (UTC),Auto-stop (UTC),Auto-destroy (UTC)
Combined Lab,summit.lab-part1,summit.lab-part2,user-combo,25,15/06/2026 09:00,15/06/2026 17:00,29/06/2026 09:00
Single Lab,summit.single-lab,user-single,15,16/06/2026 10:00,16/06/2026 18:00,30/06/2026 10:00
```

Row 1 has two CI values (`summit.lab-part1` and `summit.lab-part2`) in the CI column, causing column misalignment.

### Run the expander

Call `flow_expand_multi_asset` with:
- `csv_content`: the contents of `/tmp/multi-asset.csv`

### Review the output

The tool should:
- Detect the multi-asset row
- Split it into two separate rows, one per CI
- Preserve all other fields (namespace, users, dates) for each row
- Return the expanded CSV and a report of what was expanded

Walk through the output:
- Original: 2 rows (1 multi-asset + 1 single)
- Expanded: 3 rows (2 from the multi-asset + 1 single)
- Each expanded row is a valid, self-contained workshop entry

### Verification

The expanded CSV has 3 rows. The multi-asset row was split correctly with each CI on its own row.

---

## Step 5 -- Bulk parameter update

Skip if on the conceptual track. Skipped: requires rhdp-flow-csv.

**Goal:** Apply a parameter change across multiple rows using `flow_bulk_parameter_update`.

### Use the output from Step 2

Take the transformed CSV from Step 2 (or the fixed CSV from Step 3).

### Run a bulk update

Call `flow_bulk_parameter_update` with:
- `csv_content`: the CSV from a previous step
- `column`: `CI`
- `pattern`: `summit-2026\\.` (regex matching all summit CIs)
- `replacement`: `summit-2026-boston.` (add city qualifier)

### Review the output

The tool should:
- Match all rows where the CI column contains `summit-2026.`
- Replace the matched pattern with `summit-2026-boston.`
- Return the updated CSV and a count of rows modified

Walk through the output:
- **rows_matched**: number of rows that matched the pattern
- **rows_modified**: number of rows where a replacement was made
- **updated_csv**: the modified CSV content

### Verification

All rows with `summit-2026.` in the CI column now have `summit-2026-boston.` instead. The modification count matches the expected number of rows.

---

## Step 6 -- Diff two schedules

Skip if on the conceptual track. Skipped: requires rhdp-flow-csv.

**Goal:** Compare two CSV schedules to see what changed between versions.

### Create two versions

Write the original to `/tmp/schedule-v1.csv`:

```csv
CI Name,CI,Namespace,Users,Provisioning Date (UTC),Auto-stop (UTC),Auto-destroy (UTC)
Image Mode,summit.image-mode,user-jsmith,25,15/06/2026 09:00,15/06/2026 17:00,29/06/2026 09:00
OCP Virt,summit.ocp-virt,user-jdoe,30,15/06/2026 13:00,15/06/2026 21:00,29/06/2026 13:00
Ansible,summit.ansible,user-asmith,20,16/06/2026 10:00,16/06/2026 18:00,30/06/2026 10:00
```

Write the modified version to `/tmp/schedule-v2.csv`:

```csv
CI Name,CI,Namespace,Users,Provisioning Date (UTC),Auto-stop (UTC),Auto-destroy (UTC)
Image Mode,summit.image-mode,user-jsmith,30,15/06/2026 09:00,15/06/2026 17:00,29/06/2026 09:00
OCP Virt,summit.ocp-virt,user-jdoe,30,15/06/2026 14:00,15/06/2026 22:00,29/06/2026 14:00
RHEL Workshop,summit.rhel-workshop,user-bwilson,15,16/06/2026 10:00,16/06/2026 18:00,30/06/2026 10:00
```

Changes between v1 and v2:
- Image Mode: users changed from 25 to 30
- OCP Virt: start time shifted from 13:00 to 14:00
- Ansible row removed, RHEL Workshop row added

### Run the diff

Call `flow_csv_diff` with:
- `csv_before`: contents of `/tmp/schedule-v1.csv`
- `csv_after`: contents of `/tmp/schedule-v2.csv`

### Review the output

The tool returns a structured diff with:
- **added**: rows present in v2 but not v1
- **removed**: rows present in v1 but not v2
- **modified**: rows present in both but with field changes
- **unchanged**: rows identical in both versions

Walk through each change:
- Modified: Image Mode (users 25 -> 30), OCP Virt (time shifted)
- Removed: Ansible
- Added: RHEL Workshop

### Verification

The diff correctly identifies all three types of changes: modifications, removals, and additions.

---

## Verification

Run all preflight checks again as PASS/FAIL:

```bash
PASS=0
TOTAL=4

python3 -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null && { echo "PASS: Python 3.10+"; PASS=$((PASS+1)); } || echo "FAIL: Python 3.10+"
python3 -m pip --version >/dev/null 2>&1 && { echo "PASS: pip available"; PASS=$((PASS+1)); } || echo "FAIL: pip"
python3 -c "import rhdp_flow_csv" 2>/dev/null && { echo "PASS: rhdp-flow-csv installed"; PASS=$((PASS+1)); } || echo "FAIL: rhdp-flow-csv not installed"

MCP_FOUND=false
for f in "$HOME/.claude/settings.json" .claude/settings.json .claude/settings.local.json; do
  if [ -f "$f" ] && grep -q "rhdp-flow-csv" "$f" 2>/dev/null; then
    echo "PASS: MCP server registered in $f"; PASS=$((PASS+1))
    MCP_FOUND=true
    break
  fi
done
if [ "$MCP_FOUND" = false ]; then
  echo "FAIL: MCP server not registered"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:

```
All checks passed. The rhdp-flow-csv MCP server is installed and configured.
You can now transform, fix, expand, update, and diff workshop CSVs
directly from Claude Code.
```

If any fail, tell the user which step to re-run.

---

## Challenge

```
Here's a planning spreadsheet from a real Summit session. Process it
through the full CSV pipeline:

Step 1: Transform this raw spreadsheet into a Flow-compliant CSV
        using flow_transform_runbook.

Raw spreadsheet:

  Lab Code,Title,Session Date,Session Start,Attendees,Namespace,CI
  LB2001,RHEL Image Mode,2026-06-17,08:30:00,40,user-klee-redhat-com,summit-2026.lb2001-rhel-imagemode
  LB2002,OpenShift Virtualization,2026-06-17,08:30:00,35,user-mchen-redhat-com,summit-2026.lb2002-ocp-virt
  LB2003,Ansible Lightspeed + RHEL Image Mode,2026-06-17,13:00:00,25,user-pgarcia-redhat-com,summit-2026.lb2003-ansible-lightspeed,summit-2026.lb2003-rhel-imagemode
  LB2004,OpenShift AI,2026-06-18,09:00:00,30,user-sjones-redhat-com,summit-2026.lb2004-ocp-ai

Event config: {"timezone": "US/Eastern", "target_timezone": "UTC",
               "catalog_namespace": "babylon-catalog-event",
               "naming_template": "Summit Boston-{title}"}

Step 2: Fix any date or format issues using flow_fix_csv.

Step 3: Expand any multi-asset workshops using flow_expand_multi_asset.

Step 4: Diff the final result against the original transform output
        to see what the fix and expand steps changed.

Tell me:
  1. How many rows were in the original spreadsheet vs the final output?
  2. How many auto-fixes were applied in total (transform + fix steps)?
  3. Which row was a multi-asset workshop and how many rows did it
     expand into?
```

## Challenge Verification

Check the user's answers:

1. **Original rows vs final**: The original spreadsheet has 4 rows. After expansion, the final output should have 5 rows (LB2003 splits into 2 rows because it has two CI values).

2. **Auto-fixes**: The exact count depends on the tool output. Verify the user can identify date format conversions and column remapping as the main fix categories.

3. **Multi-asset row**: LB2003 (Ansible Lightspeed + RHEL Image Mode) is the multi-asset workshop. It has two CI values (`summit-2026.lb2003-ansible-lightspeed` and `summit-2026.lb2003-rhel-imagemode`) and expands into 2 rows.

If the user's answers are correct, write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/25.done
```

Then print:

```
Module 03 complete.

You can now process any workshop CSV through the full pipeline:
  - Transform messy spreadsheets into Flow-compliant format
  - Fix date formats and missing columns automatically
  - Expand multi-asset workshops into separate rows
  - Bulk-update parameters across rows with regex
  - Diff two schedule versions to track changes

Next module: /learn-flow-04-deployment-intelligence

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
