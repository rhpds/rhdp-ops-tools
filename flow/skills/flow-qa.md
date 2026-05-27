---
name: flow-qa
description: Run QA checks on deployed workshops and present pass/fail results
user-invocable: true
argument-hint: "qa1 (setup) | qa2 (health) | qa3 (showroom, deep browser check) | both (qa1+qa2) | all (qa1+qa2+qa3) [namespace]"
---

# Flow QA

Run QA verification checks on deployed workshops and present results with actionable next steps.

## Prerequisite Check

1. Call `flow_health` -- if error, stop and report connectivity issue.

## Workflow

### Step 1: Determine QA scope

Ask the user which checks to run:
- **QA1** (setup verification): confirms workshop resources exist and are configured
- **QA2** (deployment health): checks running pods, routes, services
- **QA3** (showroom): deep browser-based check -- verifies content renders, modules navigate, service tabs load (uses flow-showroom-qa)
- **Both** (QA1 + QA2): recommended for standard checks
- **All** (QA1 + QA2 + QA3): full audit

If the user doesn't specify, default to "all".

Optionally ask if they want to limit to a specific namespace (comma-separated for multiple).

### Step 2: Run QA

Call `flow_qa_run` with the selected `qa_type` and optional `namespace`.

### Step 2b: Run showroom QA (QA3 only)

If the user selected QA3 (or "all" which includes QA3):

1. Check if `rhdp-flow-skills/scripts/showroom-qa/` exists. If not, skip this step and fall back to the standard QA3 HTTP check from `flow_qa_run`.
2. Invoke `/flow-showroom-qa --from-deploy` to run deep browser checks on all deployed showrooms.
3. Merge the showroom QA results into the overall QA results presented in Step 4.

If the showroom QA scripts are not available, report a note:
> "Note: Deep showroom QA (browser checks) skipped -- showroom QA scripts not installed. Running HTTP-level check only."

### Step 3: Get results

Call `flow_qa_results` to retrieve the check results.

### Step 4: Present results

Format results as a pass/fail summary:

```
QA Results
----------
Total checks:  <N>
Passed:        <N>
Failed:        <N>
Warnings:      <N>

Failed Checks:
  [FAIL] <namespace> -- <check_name>: <details>
         Fix: <suggested action>

  [FAIL] <namespace> -- <check_name>: <details>
         Fix: <suggested action>

Warnings:
  [WARN] <namespace> -- <check_name>: <details>
```

For each failure, suggest a concrete fix:
- Pod not running: "Check pod logs with `oc logs -n <ns> <pod>`"
- Route not found: "Verify the route exists: `oc get routes -n <ns>`"
- Service missing: "Check the deployment completed: `flow_deploy_status`"
- Showroom unreachable: "Verify the showroom URL is accessible and DNS resolves"
- Showroom content not rendering: "Run `/flow-showroom-qa <url>` for detailed browser-level diagnostics"
- Showroom module missing: "Check the Antora nav configuration in the showroom Git repo"
- Showroom service tab failing: "Verify the service pod is running in the namespace"

### Step 5: Offer follow-up

If there are failures, ask:
> "Would you like to re-run QA after fixing these issues, or extend/redeploy the affected workshops?"
