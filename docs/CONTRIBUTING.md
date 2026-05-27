# Contributing to RHDP Ops Tools

Guidelines for adding domains, modules, skills, and scripts to the RHDP Ops Tools plugin.

## Repository Structure

```
rhdp-ops-tools/
  .claude/
    commands/              # skill dispatchers and catalog
      learn-domain-NN-*.md # module dispatchers
      ops-courseware.md        # module catalog
      preflight.md         # prerequisites check
      references/
        context.md         # team-specific values
    settings.json          # MCP server configs
  domain/                  # e.g., flow/, intake/
    modules/               # learning modules
      NN-topic.md          # one file per module
    skills/                # Claude Code skills
      skill-name.md
    scripts/               # automation scripts
  docs/
    CONTRIBUTING.md        # this file
    TODO.md                # planned features
  README.md
  CLAUDE.md
```

## Adding a New Domain

A domain is a collection of related modules, skills, and scripts (e.g., Flow, Intake).

### Steps

1. **Create directory structure**:
   ```bash
   mkdir -p domain/modules domain/skills domain/scripts
   ```

2. **Add at least one module** (see "Adding a Module" below)

3. **Create dispatchers** in `.claude/commands/`:
   ```bash
   touch .claude/commands/learn-domain-01-topic.md
   ```

4. **Update catalog** in `.claude/commands/ops-courseware.md`:
   - Add domain section with module table
   - Add routing entries to Module Routing Table
   - Update module count in footer

5. **Update README.md**:
   - Add domain to Domains section
   - Document modules, skills, and scripts

6. **Commit**:
   ```bash
   git add domain/ .claude/commands/ README.md
   git commit -m "add domain: domain-name"
   ```

## Adding a Skill

Skills are reusable Claude Code commands for specific operations.

### Steps

1. **Create skill file**:
   ```bash
   touch domain/skills/skill-name.md
   ```

2. **Follow skill structure**:
   - Title (# Skill Name)
   - Purpose
   - Prerequisites
   - Usage
   - Parameters
   - Examples
   - See also

3. **Document in README** if user-facing

4. **Commit**:
   ```bash
   git add domain/skills/skill-name.md README.md
   git commit -m "add skill: skill-name"
   ```

## Adding a Module

Modules are interactive learning experiences.

### Steps

1. **Create module file**:
   ```bash
   touch domain/modules/NN-topic.md
   ```
   
   Use next available number (NN = 01, 02, etc.)

2. **Follow module structure**:
   - Quick Setup
   - Orientation
   - Preflight (EXISTS/MISSING checks)
   - Steps (with verification)
   - Verification (all-green check)
   - Challenge (hands-on task)
   - Challenge Verification

3. **Create dispatcher**:
   ```bash
   touch .claude/commands/learn-domain-NN-topic.md
   ```
   
   Template:
   ```markdown
   # Module Title
   
   Brief description.
   Estimated time: XX minutes. Prerequisites: ...
   
   Read domain/modules/NN-topic.md but present it in phases:
   
   Phase 1: Read only the Quick Setup and Orientation sections. Present them.
            Ask: "Ready to check prerequisites?"
   
   Phase 2: Read only the Preflight section. Run the checks.
            Skip any step that passes. Report results.
            Ask: "Ready to start the walkthrough?"
   
   Phase 3: Read and present one Step at a time.
            After each step's verification passes, proceed to the next.
            Do not read ahead -- load each step only when needed.
   
   Phase 4: Read only the Verification section. Run all checks.
            Report results.
   
   Phase 5: Read only the Challenge and Challenge Verification sections.
            Present the challenge. After the user completes it, verify.
   
   Use .claude/commands/references/context.md for team-specific values.
   Track progress in ~/.claude/courseware-progress/.
   ```

4. **Update catalog** (`.claude/commands/ops-courseware.md`):
   - Add row to domain module table
   - Add routing entry to Module Routing Table
   - Update total time calculation
   - Update module count

5. **Update README.md**:
   - Add row to domain module table
   - Update total time

6. **Commit**:
   ```bash
   git add domain/modules/NN-topic.md .claude/commands/ README.md
   git commit -m "add module NN: topic name"
   ```

## Commit Message Guidelines

### Rules
- Use plain English describing what changed
- NO conventional-commit prefixes (`feat:`, `fix:`, `chore:`, etc.)
- NO emojis or emoticons
- Be specific and concise

### Examples

Good:
```
add module 03: CSV pipeline
update flow-deploy skill with pool support
fix preflight check for Python 3.10 detection
```

Bad:
```
feat: add module 03 for CSV pipeline
fix(flow): update flow-deploy skill with pool support
chore: fix preflight check
```

## Pull Request Process

1. **Create branch** for your changes:
   ```bash
   git checkout -b feature/description
   ```

2. **Make changes** following guidelines above

3. **Run validation** if available:
   ```bash
   python3 scripts/validate.py
   ```

4. **Commit** with clear messages

5. **Push and create PR**:
   ```bash
   git push -u origin feature/description
   ```

6. **PR description should include**:
   - What changed
   - Why it changed
   - Any new dependencies
   - Testing done

7. **Review and merge** after approval

## Code Style

### Markdown
- Use ATX-style headers (`#`)
- Use fenced code blocks with language tags
- Use tables for structured data
- Keep line length reasonable (wrap at ~100 chars)

### Bash Scripts
- Use `#!/bin/bash` shebang
- Add comments for complex logic
- Use shellcheck if available
- Handle errors (set -e, check exit codes)

### Python Scripts
- Follow PEP 8
- Use type hints where helpful
- Add docstrings for functions
- Use Black formatter if available

## Versioning

This project uses semantic versioning (semver).

| Bump  | When |
|-------|------|
| Major | Breaking changes: module restructuring, incompatible renames |
| Minor | New module, new skill, new domain |
| Patch | Fixes or edits to existing content |

Tag releases:
```bash
git tag -a vX.Y.Z -m "description of release"
git push --tags
```

## Questions?

- Check existing modules in `flow/modules/` for examples
- Review skills in `flow/skills/` for patterns
- Open an issue for clarification
- Contact the RHDP operations team
