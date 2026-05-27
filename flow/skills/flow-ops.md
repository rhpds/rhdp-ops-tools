---
name: flow-ops
description: Workshop operations -- lock, extend, scale, or disable autostop
user-invocable: true
argument-hint: "lock | unlock | extend <days>d <hours>h | extend-destroy <days>d | scale <count> | disable-autostop [ci_filter]"
---

# Flow Ops

Perform operations on deployed workshops: lock, unlock, extend stop/destroy times, scale seats, or disable autostop.

## Prerequisite Check

1. Call `flow_health` -- if error, stop and report connectivity issue.

## Workflow

### Step 1: Detect operation type

Ask the user what they want to do, or infer from their message:

| User says | Action |
|-----------|--------|
| "lock", "lock workshops" | `lock` |
| "unlock", "unlock workshops" | `unlock` |
| "extend", "extend stop", "more time" | `extend-stop` |
| "extend destroy", "delay teardown" | `extend-destroy` |
| "scale", "add seats", "more users" | `scale` |
| "disable autostop", "keep running" | `disable-autostop` |

### Step 2: Gather parameters

Based on the action:

**lock / unlock / disable-autostop:**
- Optional: catalog item filter (`ci_filter`)

**extend-stop / extend-destroy:**
- Days to extend (default 0)
- Hours to extend (default 0)
- Optional: catalog item filter

**scale:**
- Target instance count (required)
- Optional: catalog item filter

If a catalog item filter is needed, call `flow_catalog_items` to help the user pick.

### Step 3: Confirm the operation

Show a preview:

```
Operation Preview
-----------------
Action:        <action>
Target:        <all workshops / filtered by CI>
Parameters:    <days/hours/count as applicable>
```

Ask: "Proceed with this operation?"

### Step 4: Execute

Call `flow_operations` with:
- `action`: the operation type
- `ci_filter`: if specified
- `days`/`hours`: for extend operations
- `target_count`: for scale

### Step 5: Report results

Show the result:

```
Operation Complete
------------------
Action:   <action>
Success:  <true/false>
Message:  <server message>
```

If the operation failed, suggest troubleshooting steps.
