# Preflight Check

Verify prerequisites for RHDP Ops Tools modules.

Run this check before starting any module to ensure your environment is ready.

## Checks

```bash
#!/bin/bash

PASS_COUNT=0
FAIL_COUNT=0
INFO_COUNT=0

echo "Running preflight checks..."
echo ""

# Check 1: Claude Code installed
if command -v claude &> /dev/null; then
  echo "[PASS] Claude Code installed"
  ((PASS_COUNT++))
else
  echo "[FAIL] Claude Code not installed"
  ((FAIL_COUNT++))
fi

# Check 2: Python 3.10+
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -ge 3 ]] && [[ "$PYTHON_MINOR" -ge 10 ]]; then
  echo "[PASS] Python $PYTHON_VERSION (>= 3.10)"
  ((PASS_COUNT++))
else
  echo "[FAIL] Python $PYTHON_VERSION (need >= 3.10)"
  ((FAIL_COUNT++))
fi

# Check 3: rhdp-flow-mcp installed
if python3 -c "import rhdp_flow_mcp" &> /dev/null; then
  echo "[PASS] rhdp-flow-mcp installed"
  ((PASS_COUNT++))
else
  echo "[FAIL] rhdp-flow-mcp not installed"
  ((FAIL_COUNT++))
fi

# Check 4: rhdp-flow-csv installed
if python3 -c "import rhdp_flow_csv" &> /dev/null; then
  echo "[PASS] rhdp-flow-csv installed"
  ((PASS_COUNT++))
else
  echo "[FAIL] rhdp-flow-csv not installed"
  ((FAIL_COUNT++))
fi

# Check 5: rhdp-flow-intel installed
if python3 -c "import rhdp_flow_intel" &> /dev/null; then
  echo "[PASS] rhdp-flow-intel installed"
  ((PASS_COUNT++))
else
  echo "[FAIL] rhdp-flow-intel not installed"
  ((FAIL_COUNT++))
fi

# Check 6: playwright installed (INFO only)
if python3 -c "import playwright" &> /dev/null; then
  echo "[INFO] playwright installed (for showroom QA)"
  ((INFO_COUNT++))
else
  echo "[INFO] playwright not installed (optional, for showroom QA)"
  ((INFO_COUNT++))
fi

echo ""
echo "---"
echo "Summary: $PASS_COUNT passed, $FAIL_COUNT failed, $INFO_COUNT info"
echo "---"
```

## Guidance

**All checks pass?**
Run `/courseware` to see available modules.

**Missing MCP servers?**
Run the automated setup script:
```bash
bash flow/scripts/setup-all.sh
```

This will install all three Flow MCP servers (rhdp-flow-mcp, rhdp-flow-csv, rhdp-flow-intel) and configure them in your Claude Code settings.

**Missing playwright?**
Optional for showroom QA automation. Install with:
```bash
pip install playwright
playwright install chromium
```

---

After installation, re-run `/preflight` to verify.
