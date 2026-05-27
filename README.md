# RHDP Ops Tools

Interactive learning modules, skills, and MCP servers for RHDP operations. A Claude Code plugin for workshop automation, deployment monitoring, and intake workflows.

## Getting Started

### Plugin Install (Recommended)

```bash
claude plugin add github:rhpds/rhdp-ops-tools
```

This gives you:
- 5 Flow modules for workshop automation
- 10 Flow skills for daily operations
- 3 MCP servers (rhdp-flow, rhdp-flow-csv, rhdp-flow-intel)
- Automated setup scripts
- Showroom QA automation

### Standalone Clone

For development or customization:

```bash
git clone https://github.com/rhpds/rhdp-ops-tools.git ~/repos/rhdp-ops-tools
cd ~/repos/rhdp-ops-tools
```

## Prerequisites Check

Before starting, verify your environment:

```
/preflight
```

This checks for:
- Claude Code installed
- Python 3.10+
- MCP servers (rhdp-flow-mcp, rhdp-flow-csv, rhdp-flow-intel)
- Playwright (optional, for showroom QA)

If MCP servers are missing, run the automated installer:

```bash
bash flow/scripts/setup-all.sh
```

## Domains

### Flow -- Workshop Automation

Interactive modules teaching workshop deployment, operations, CSV processing, and monitoring.

| # | Module | Time | Description |
|---|--------|------|-------------|
| `01` | RHDP-Flow MCP | 20 min | Install and use the RHDP-Flow MCP server |
| `02` | RHDP-Flow Ops | 15 min | Daily workshop operations with Flow skills |
| `03` | CSV Pipeline | 20 min | Transform and validate workshop CSVs |
| `04` | Deployment Intelligence | 20 min | Monitor deployments, detect ghost workshops |
| `05` | Event-Scale Operations | 30 min | Multi-day event simulation (capstone) |

**Total: 105 minutes**

Start with:
```
/courseware
```

Then launch a module:
```
/learn-flow-01
```

### Intake -- Workshop Intake (Coming Soon)

Modules for workshop intake and provisioning workflows.

## How Modules Work

Each module follows a structured learning path:

1. **Orientation** — What you'll learn and why it matters
2. **Preflight** — Audit current state, skip what's already done
3. **Steps** — Guided walkthrough with verification at each step
4. **Verification** — All-green final check
5. **Challenge** — Hands-on task using real team data
6. **Challenge Verification** — Confirm your results

Modules are self-paced and track progress in `~/.claude/courseware-progress/`.

## MCP Servers

This plugin provides three MCP servers for workshop operations:

| Server | Package | Purpose |
|--------|---------|---------|
| **rhdp-flow** | `rhdp-flow-mcp` | Workshop deployment and management via Flow API |
| **rhdp-flow-csv** | `rhdp-flow-csv` | CSV transformation pipeline (no backend required) |
| **rhdp-flow-intel** | `rhdp-flow-intel` | Deployment monitoring and diagnostics |

All three are installed automatically via:
```bash
bash flow/scripts/setup-all.sh
```

## Skills

Flow skills for daily operations:

- `flow-deploy` — Deploy workshops from CSV schedules
- `flow-ops` — Lock, unlock, extend, scale workshops
- `flow-bulk` — Bulk operations on multiple workshops
- `flow-status` — Monitor deployment status
- `flow-report` — Generate QA and deployment reports
- `flow-qa` — Run QA checks (setup, deployment, showroom)
- `flow-showroom-qa` — Deep Showroom QA with Playwright
- `flow-csv-pipeline` — Transform CSVs, fix formatting, diff schedules
- `flow-event-prep` — Pre-deployment checklist and validation
- `flow-summit-deploy` — Summit-specific deployment workflow

See `flow/skills/` for full skill definitions.

## Scripts

- `flow/scripts/setup-all.sh` — Install all MCP servers and configure Claude Code
- `flow/scripts/showroom-qa/` — Playwright-based Showroom QA automation

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- How to add a new domain
- How to add a skill
- How to add a module
- Commit message guidelines
- PR process

## License

MIT

## Support

For issues or questions:
- Open an issue: https://github.com/rhpds/rhdp-ops-tools/issues
- Contact: RHDP operations team
