# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What This Repo Does

RHDP Ops Tools is a Claude Code plugin providing interactive learning modules, skills, and MCP servers for the RHDP operations team. It packages workshop automation, deployment monitoring, and intake workflows into a single toolkit.

This repo can be used:
- **As a plugin**: `claude plugin add github:rhpds/rhdp-ops-tools`
- **As a standalone clone**: for development or customization

## Repository Structure

```
rhdp-ops-tools/
  .claude/
    commands/              # skill dispatchers and catalog
      learn-flow-NN-*.md   # module dispatchers
      courseware.md        # module catalog
      preflight.md         # prerequisites check
      references/
        context.md         # team-specific values
    settings.json          # MCP server configs
  flow/                    # Flow domain (workshop automation)
    modules/               # learning modules
      NN-topic.md          # one file per module
    skills/                # Claude Code skills
      flow-*.md
    scripts/               # automation scripts
      setup-all.sh         # install all MCP servers
      showroom-qa/         # Playwright-based QA automation
  intake/                  # Intake domain (coming soon)
  docs/
    CONTRIBUTING.md        # authoring guide
    TODO.md                # planned features
  README.md                # user-facing overview
  CLAUDE.md                # this file
```

## Domain Organization

This repo is organized by **domain** (Flow, Intake, etc.). Each domain contains:
- **modules/** — interactive learning content
- **skills/** — Claude Code skill definitions
- **scripts/** — automation scripts and utilities

To add a new domain:
1. Create `domain/` directory
2. Add `domain/modules/`, `domain/skills/`, `domain/scripts/`
3. Create dispatchers in `.claude/commands/learn-domain-NN-*.md`
4. Update `.claude/commands/courseware.md` catalog
5. Update README.md domain table

## Key Conventions

### Module Structure
Each module follows this pattern:
1. **Quick Setup** — one-line install command
2. **Orientation** — what you'll learn
3. **Preflight** — audit current state, skip what's done
4. **Steps** — guided walkthrough with verification
5. **Verification** — all-green final check
6. **Challenge** — hands-on task with real data
7. **Challenge Verification** — confirm results

### Writing Rules
- No conventional-commit prefixes in commit messages or PR titles
- No emojis or emoticons in any output
- Plain English commit messages describing what changed
- Dispatchers are thin (load module content, track progress)

## Versioning

This project uses semver tags on the `main` branch.

| Bump  | When |
|-------|------|
| Major | Breaking changes: module restructuring, incompatible skill/command renames |
| Minor | New module added, new skill/command added, new domain added |
| Patch | Fixes or edits to existing modules, skills, commands, or docs |

Tag format: `vX.Y.Z` (e.g. `v1.0.0`). Create annotated tags:
```
git tag -a vX.Y.Z -m "description of release"
```

## Adding Components

### New Module
1. Create `domain/modules/NN-topic.md` following the structure above
2. Create `.claude/commands/learn-domain-NN-topic.md` as dispatcher
3. Add to `.claude/commands/courseware.md` catalog
4. Update README.md module table
5. Commit: "add module NN: topic name"

### New Skill
1. Create `domain/skills/skill-name.md`
2. Document in domain README if applicable
3. Commit: "add skill: skill-name"

### New Domain
1. Create `domain/` with `modules/`, `skills/`, `scripts/`
2. Create dispatcher pattern in `.claude/commands/`
3. Update catalog and README
4. Commit: "add domain: domain-name"

## Workflow

- Development happens on `main` branch
- Tag releases after module or skill additions
- No conventional-commit prefixes, no emojis in any output
- Always run automated tests if available
- Update courseware catalog after changes

## MCP Servers

This plugin provides three MCP servers:

| Server | Package | Purpose |
|--------|---------|---------|
| rhdp-flow | `rhdp-flow-mcp` | Workshop deployment and management |
| rhdp-flow-csv | `rhdp-flow-csv` | CSV transformation pipeline |
| rhdp-flow-intel | `rhdp-flow-intel` | Deployment monitoring and diagnostics |

All three are installed via `flow/scripts/setup-all.sh`.
