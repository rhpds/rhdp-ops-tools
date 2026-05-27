#!/usr/bin/env bash
set -euo pipefail

# One-shot idempotent setup for all RHDP-Flow MCP servers, skills, and agents.
# Safe to re-run -- skips anything already installed.

PLUGIN_REPO="$HOME/.claude/plugins/rhdp-ops-tools/repo"
SETTINGS="$HOME/.claude/settings.json"
PASS=0
FAIL=0
SKIP=0

log_pass() { echo "  PASS: $1"; PASS=$((PASS+1)); }
log_fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
log_skip() { echo "  SKIP: $1 (already done)"; SKIP=$((SKIP+1)); }

echo "RHDP-Flow Setup"
echo "==============="
echo ""

# --- Dependency check ---
echo "Checking dependencies..."
python3 -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null || { echo "  FAIL: Python 3.10+ required"; exit 1; }
log_pass "Python $(python3 --version 2>&1 | awk '{print $2}')"
python3 -m pip --version >/dev/null 2>&1 || { echo "  FAIL: pip required"; exit 1; }
log_pass "pip available"
echo ""

# --- Detect install base ---
if [ -d "$PLUGIN_REPO" ]; then
  BASE="$PLUGIN_REPO"
  echo "Install source: courseware plugin ($BASE)"
else
  BASE="$(pwd)"
  echo "Install source: local repo ($BASE)"
fi
echo ""

# --- Install Python packages ---
echo "Installing Python packages..."
for pkg in rhdp-flow-mcp rhdp-flow-csv rhdp-flow-intel; do
  module=$(echo "$pkg" | tr '-' '_')
  if python3 -c "import $module" 2>/dev/null; then
    log_skip "$pkg"
  elif [ -d "$BASE/$pkg" ]; then
    pip install -e "$BASE/$pkg" -q 2>/dev/null && log_pass "$pkg installed" || log_fail "$pkg install failed"
  else
    log_fail "$pkg not found at $BASE/$pkg"
  fi
done
echo ""

# --- Write MCP server configs ---
echo "Registering MCP servers in $SETTINGS..."
python3 << 'PYEOF'
import json, os, shutil

path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
settings.setdefault("mcpServers", {})
py = shutil.which("python3")

servers = {
    "rhdp-flow": {
        "command": py,
        "args": ["-m", "rhdp_flow_mcp"],
        "env": {"FLOW_API_URL": "http://localhost:8000"},
    },
    "rhdp-flow-csv": {
        "command": py,
        "args": ["-m", "rhdp_flow_csv"],
    },
    "rhdp-flow-intel": {
        "command": py,
        "args": ["-m", "rhdp_flow_intel"],
        "env": {"FLOW_API_URL": "http://localhost:8000"},
    },
}

added = []
skipped = []
for name, config in servers.items():
    if name in settings["mcpServers"]:
        skipped.append(name)
    else:
        settings["mcpServers"][name] = config
        added.append(name)

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

for s in skipped:
    print(f"  SKIP: {s} (already registered)")
for a in added:
    print(f"  PASS: {a} registered")
PYEOF
echo ""

# --- Symlink skills and agents into plugin directory ---
PLUGIN_DIR="$HOME/.claude/plugins/rhdp-ops-tools"
if [ -d "$PLUGIN_DIR" ]; then
  echo "Linking skills and agents into plugin..."

  mkdir -p "$PLUGIN_DIR/skills" "$PLUGIN_DIR/agents"

  # Skills
  if [ -d "$PLUGIN_REPO/flow/skills" ]; then
    for f in "$PLUGIN_REPO/flow/skills"/flow-*.md; do
      [ -f "$f" ] || continue
      target="$PLUGIN_DIR/skills/$(basename "$f")"
      if [ -L "$target" ] || [ -f "$target" ]; then
        log_skip "skill $(basename "$f")"
      else
        ln -sf "$f" "$target" && log_pass "skill $(basename "$f") linked" || log_fail "skill $(basename "$f")"
      fi
    done
  else
    echo "  SKIP: rhdp-flow-skills not found in plugin repo"
  fi

  # Agents
  if [ -d "$PLUGIN_REPO/flow/agents" ]; then
    for f in "$PLUGIN_REPO/flow/agents"/flow-*.md; do
      [ -f "$f" ] || continue
      target="$PLUGIN_DIR/agents/$(basename "$f")"
      if [ -L "$target" ] || [ -f "$target" ]; then
        log_skip "agent $(basename "$f")"
      else
        ln -sf "$f" "$target" && log_pass "agent $(basename "$f") linked" || log_fail "agent $(basename "$f")"
      fi
    done
  else
    echo "  SKIP: rhdp-flow-agents not found in plugin repo"
  fi
else
  echo "Skipping symlinks: courseware plugin not installed."
  echo "  Install with: claude plugin add github:rhpds/rhdp-ops-tools"
fi
echo ""

# --- Summary ---
TOTAL=$((PASS+FAIL+SKIP))
echo "Done: $PASS installed, $SKIP skipped, $FAIL failed (out of $TOTAL items)."
if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "Some items failed. Check the output above for details."
  exit 1
fi
echo ""
echo "Restart Claude Code to activate the new MCP servers."
