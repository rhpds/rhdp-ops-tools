---
name: flow-showroom-qa
description: Run deep browser-based QA checks on RHDP workshop showrooms -- verifies content renders, modules navigate, service tabs load
user-invocable: true
argument-hint: "<url> [--level simple|login|state] | --from-deploy | --craft <url>"
---

# Flow Showroom QA

Run end-to-end browser-based QA checks on RHDP workshop showrooms. Goes beyond HTTP accessibility -- verifies content renders, modules are navigable, credentials are visible, and service tabs load.

## Prerequisite Check

1. Verify `rhdp-flow-skills/scripts/showroom-qa/` directory exists. If not, stop and report: "Showroom QA scripts not found. Install the rhdp-flow-skills plugin or check your working directory."
2. Verify `playwright` is installed: run `python3 -c "import playwright"`. If it fails, stop and report: "Playwright is not installed. Run: pip install playwright && playwright install chromium"

## Workflow

### Step 1: Determine target showrooms

Parse the user's arguments:

- **Single URL** (e.g., `/flow-showroom-qa https://showroom-...`): Use that URL directly. Ask the user for credentials (username and password).
- **`--from-deploy`**: Call `flow_deploy_status` to get current deployment results. Extract showroom URLs by finding service URLs matching the pattern `*-showroom.*` in each namespace. Ask the user for the common password (username is derived from the namespace, typically `user-<id>`).
- **`--craft <url>`**: This mode generates a new QA script for an unknown showroom variant. Requires the Webwright plugin. Delegate to `/webwright:craft` with the standard QA prompt template (see the Craft Mode section below). Save the output to `rhdp-flow-skills/scripts/showroom-qa/`. Stop after generation -- do not run QA.

If no argument is provided, ask: "Provide a showroom URL, or use --from-deploy to check all deployed showrooms."

### Step 2: Detect showroom variant

For each target URL, detect the variant by navigating to the URL with Playwright MCP and inspecting the DOM:

1. Navigate to the URL using `browser_navigate`
2. Take a snapshot using `browser_snapshot`
3. Check for Antora fingerprints:
   - Content is inside an iframe
   - The iframe contains a `nav-toggle` button or `.nav-list` element
   - An `article` element with Asciidoc-generated structure exists
   - Footer contains "Powered by" with a link to demo.redhat.com
4. If Antora fingerprints match, variant = `antora`
5. If no known variant matches, report: "Unknown showroom variant at <url>. Use --craft <url> to generate a QA script for this variant."

### Step 3: Run QA script

Execute the matching script. For the `antora` variant:

Determine the QA level:
- User asked for a quick check or didn't specify: `--level simple`
- User wants to verify logins work: `--level login`
- Pre-event deep validation: `--level state`

```bash
python3 rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py \
  --url "<showroom_url>" \
  --level "<level>" \
  --output-dir "showroom-qa-results/<namespace_or_timestamp>"
```

Only add `--user` and `--pass` if the script cannot auto-extract credentials from the showroom page.

Capture both stdout (JSON report) and the exit code.

### Step 4: Parse and format results

Parse the JSON report from stdout. Format results in the standard flow-qa table:

```
Showroom QA Results
-------------------
URL:      <url>
Variant:  <variant>
Total:    <N> checks
Passed:   <N>
Failed:   <N>

Passed Checks:
  [PASS] page_load -- Page loaded with title "<title>"
  [PASS] module_list -- Found <N> modules
  [PASS] module_1_content -- "Module 1: The Problem Domain" rendered
  ...

Failed Checks:
  [FAIL] <check_name> -- <error message>
         Fix: <suggested action based on check type>

Screenshots saved to: showroom-qa-results/<dir>/
```

Suggested fixes per check type:
- `page_load` fail: "Verify the showroom URL is correct and the route exists"
- `module_list` fail: "Check the Antora navigation configuration in the showroom repo"
- `module_*_content` fail: "Verify the module page exists and Antora build completed"
- `tab_*_load` fail: "Check that the service is running in the namespace"
- `tab_*_login` fail: "Verify credentials are correct and the service accepts login"

### Step 5: Offer follow-up

If there are failures:
> "Would you like to re-run QA after fixing issues, or view the screenshots for failed checks?"

If all pass:
> "All showroom QA checks passed. Screenshots saved to <dir> for evidence. Open report.html for a visual summary."

If multiple showrooms were checked (--from-deploy mode), present a summary table:

```
Showroom QA Summary (--from-deploy)
------------------------------------
  [PASS] namespace-1  https://showroom-...  15/15 checks passed
  [FAIL] namespace-2  https://showroom-...  13/15 checks passed
  [PASS] namespace-3  https://showroom-...  15/15 checks passed

Overall: 2/3 showrooms fully passing
```

## Craft Mode

When invoked with `--craft <url>`, generate a new variant script using Webwright:

1. Check that the Webwright plugin is available (try invoking `/webwright:craft --help`). If not available, stop and report: "Webwright plugin is required for --craft mode. Install with: /plugin marketplace add microsoft/Webwright && /plugin install webwright@webwright"
2. Navigate to the URL to understand the showroom structure
3. Invoke `/webwright:craft` with the standard QA prompt (adapted for the specific showroom's DOM structure)
4. Save the generated script to `rhdp-flow-skills/scripts/showroom-qa/showroom-qa-<variant>.py`
5. Report: "Generated QA script for <variant> variant. Review the script, test it, and commit."
