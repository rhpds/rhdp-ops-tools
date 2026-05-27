---
name: flow-csv-pipeline
description: Guided CSV pipeline -- transform, fix, expand, validate, deploy
user-invocable: true
argument-hint: "<spreadsheet_path> [event_name] [source_timezone] [catalog_namespace] [naming_template]"
---

# Flow CSV Pipeline

End-to-end workflow for preparing a workshop CSV from a raw planning spreadsheet.

## Prerequisite Check

1. Verify `rhdp-flow-csv` MCP server is available (try calling `flow_fix_csv` on any file)
2. If available, also check `rhdp-flow-mcp` for validation (call `flow_health`)
3. If neither is available, stop and tell the user which MCP servers to install

## Workflow

### Step 1: Source spreadsheet

Ask the user for the path to their planning spreadsheet (CSV or similar).

### Step 2: Event configuration

Ask these one at a time:
- **Event name**: e.g., "Summit 2026 Day 3"
- **Source timezone**: what timezone are the dates in? (BST, EST, UTC, etc.)
- **Catalog namespace**: default catalog namespace (e.g., `babylon-catalog-event`)
- **Naming template**: how to name workshops (e.g., "Day {day}-Test-{title}")
- **User mapping**: which emails map to which namespaces? (can skip if namespaces are already correct)
- **Exclude users**: any usernames to exclude from the output?

### Step 3: Transform

Call `flow_transform_runbook` with the collected config. Show the transformation report:
- Rows processed vs output
- Auto-fixes applied (suffix additions, date conversions)
- Warnings to review

### Step 4: Fix

Call `flow_fix_csv` on the output. Show any issues found and whether they were auto-fixed.

### Step 5: Multi-asset check

Call `flow_expand_multi_asset` on the output. Show any expansions detected and corrected.

### Step 6: Validate (requires Flow API)

If `rhdp-flow-mcp` is available:
1. Call `flow_upload_csv` with the prepared CSV
2. Call `flow_validate` with check="all"
3. Show validation results

If not available, skip and tell the user to validate manually.

### Step 7: Next steps

Ask: "CSV is ready. Would you like to dry-run deploy, or stop here?"
- If dry-run: call `flow_deploy` with `dry_run=true`
- If stop: show the output file path

## Output

```
CSV Pipeline Summary
--------------------
Source:       <source_path>
Output:       <output_path>
Rows:         <N> processed, <M> output
Auto-fixes:   <count> applied
Validation:   <PASS/FAIL/SKIPPED>
Status:       Ready to deploy / Needs attention
```
