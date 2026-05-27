# rhdp-flow-skills

Claude Code skills plugin for RHDP-Flow workshop operations. Provides guided workflows that wrap the `rhdp-flow-mcp` tools.

## Requirements

- `rhdp-flow-mcp` must be installed and configured

## Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `flow-deploy` | "deploy workshops" | Guided CSV generation, validation, dry-run, and deploy |
| `flow-qa` | "run QA", "check workshops" | Run QA checks with pass/fail summary and fix suggestions |
| `flow-showroom-qa` | "check showroom", "showroom QA" | Deep browser-based showroom QA: content, modules, tabs, login |
| `flow-ops` | "extend workshop", "lock", "scale" | Lock, extend, scale, or disable autostop on workshops |
| `flow-status` | "workshop status" | Deployment, QA, and pool availability dashboard |
| `flow-bulk` | "deploy N workshops" | Bulk staggered deployments for events and load tests |
| `flow-report` | "generate report" | Formatted reports for Slack, email, or stakeholders |

## Install

Install the rhdp-ops-tools plugin: `claude plugin install rhpds/rhdp-ops-tools`

## Scripts

The `scripts/` directory contains standalone tools that skills depend on:

| Directory | Description |
|-----------|-------------|
| `scripts/showroom-qa/` | Playwright-based showroom QA scripts (one per variant) |

Scripts run independently -- no Claude Code or Webwright required. See each directory's README for usage.
