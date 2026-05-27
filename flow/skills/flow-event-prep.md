---
name: flow-event-prep
description: Multi-day event preparation -- CSV pipeline per day, pool demand, readiness report
user-invocable: true
argument-hint: "<event_name> <num_days> [catalog_namespace] [naming_template]"
---

# Flow Event Prep

End-to-end workflow for preparing a multi-day event (like Red Hat Summit).

## Prerequisite Check

1. Verify `rhdp-flow-csv` MCP server is available
2. Check `rhdp-flow-mcp` for pool and catalog checks (call `flow_health`)
3. If neither is available, stop and show install instructions

## Workflow

### Step 1: Event details

Ask these one at a time:
- **Event name**: e.g., "Red Hat Summit 2026"
- **Number of days**: how many days of workshops?
- **Catalog namespace**: default `babylon-catalog-event`
- **Naming template**: e.g., "Day {day}-Test-{title}"

### Step 2: Per-day spreadsheets

For each day, ask the user for the path to the planning spreadsheet.

### Step 3: Per-day pipeline

For each day's spreadsheet, run the CSV pipeline:
1. Call `flow_transform_runbook` with the event config (set day number in naming template)
2. Call `flow_fix_csv` on the output
3. Call `flow_expand_multi_asset` on the output
4. Show per-day summary

### Step 4: Aggregate pool demand

If `rhdp-flow-mcp` is available:
1. Read all transformed CSVs
2. Count unique CI values and total seat demand
3. Call `flow_pools` to get current availability
4. Compare demand vs supply
5. Flag any shortfalls

If not available, produce a manual demand estimate.

### Step 5: Combined readiness report

Produce a combined report:
```
Event Readiness: <Event Name>
================================
Day 1: <N> workshops, <M> seats -- <READY/ISSUES>
Day 2: <N> workshops, <M> seats -- <READY/ISSUES>
...

Pool Summary:
  <CI>: <demand> needed, <available> ready -- <OK/SHORTFALL>
  ...

Overall: <READY TO DEPLOY / NEEDS ATTENTION>
  <list specific issues if any>
```

### Step 6: Next steps

Ask: "Event CSVs are prepared. Options:"
1. Deploy a single day (specify which)
2. Deploy all days
3. Stop here and review CSVs manually
