# Showroom QA Scripts

Standalone Playwright scripts that perform end-to-end QA checks on RHDP workshop showrooms. Each script targets a specific showroom variant.

No Claude Code, Webwright, or API keys required.

## Quick Start

**Step 1 -- Install Python dependencies**

You need Python 3.10+ and Playwright with Chromium.

```bash
pip install playwright
playwright install chromium
```

If `pip` installs to a location not on your `$PATH`, use `pip install --user playwright` or a virtual environment.

**Step 2 -- Run the script**

Point it at your showroom URL:

```bash
python3 showroom-qa-antora.py \
  --url "https://showroom-user-xxxxx-showroom.apps.cluster-xxxxx.dyn.redhatworkshops.io/"
```

That's it. The script runs all four QA phases (page load, content, module walkthrough, service tabs) and prints a JSON report to stdout. An HTML report with embedded screenshots is generated in the output directory.

**Step 3 -- Check the results**

- Exit code `0` = all checks passed
- Exit code `1` = at least one check failed
- Open `./showroom-qa-results/report.html` in a browser for a visual report with screenshots
- Screenshots are also available individually in `./showroom-qa-results/`

## QA Levels

The `--level` flag controls how deep the QA goes. Each level includes everything from the level above it.

| Level | What it checks |
|-------|---------------|
| `simple` | Page loads, content renders, modules navigate, tab iframes load (default) |
| `login` | + Submits credentials to login-gated tabs (AAP2, Kira, OpenShift, etc.), verifies login succeeds |
| `state` | + Verifies post-login content (dashboards are populated, no error pages, services are responsive) |
| `full` | Reserved for future use (instruction execution) |

```bash
# Quick pre-event check
python3 showroom-qa-antora.py --url "https://showroom-..." --level simple

# Verify all service logins work
python3 showroom-qa-antora.py --url "https://showroom-..." --level login

# Deep validation before go-live
python3 showroom-qa-antora.py --url "https://showroom-..." --level state
```

## Credentials

Credentials are **optional**. The script auto-extracts username and password from the showroom landing page when they're displayed in the credentials box.

If the showroom doesn't display credentials on the landing page, provide them manually:

```bash
python3 showroom-qa-antora.py \
  --url "https://showroom-..." \
  --user "user-xxxxx" \
  --pass "your-password" \
  --level login
```

At `simple` level, credentials are not needed at all. At `login` and `state` levels, if a tab has a login gate and no credentials are available, that check fails with a clear message.

## Arguments

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--url` | Yes | -- | Showroom URL |
| `--user` | No | auto-extracted | Login username |
| `--pass` | No | auto-extracted | Login password |
| `--level` | No | `simple` | QA depth: simple, login, state, full |
| `--output-dir` | No | `./showroom-qa-results` | Screenshot and report output directory |
| `--checks` | No | all | Comma-separated phases to run (see below) |
| `--headed` | No | off | Run browser in headed mode (visible window) |
| `--no-html` | No | off | Skip HTML report generation |

### Check Phases

| Phase | What it verifies |
|-------|-----------------|
| `page_load` | HTTP 200, page title, landing page renders |
| `content` | Content iframe loads, module list in sidebar, credentials box visible |
| `modules` | Each module link navigates, has H1 heading and body content |
| `tabs` | Tab iframe checks, login submission (at `login`+), state verification (at `state`) |

Run specific phases with `--checks`:

```bash
python3 showroom-qa-antora.py --url "..." --checks "page_load,content"
```

## HTML Report

By default, the script generates a self-contained HTML report at `{output-dir}/report.html`. The report includes:

- Pass/fail summary banner
- Each check with status, details, and expandable screenshot
- All screenshots embedded as base64 (no external files needed)

Open it in any browser. Share it with anyone -- no server or special tools needed.

Skip with `--no-html` if you only want JSON output.

## Available Scripts

| Script | Variant | Description |
|--------|---------|-------------|
| `showroom-qa-antora.py` | Antora | Split-panel showroom with Antora docs + service tabs |

## Output

**JSON report** to stdout:

```json
{
  "url": "https://showroom-...",
  "variant": "antora",
  "level": "login",
  "timestamp": "2026-05-24T12:00:00Z",
  "checks": [
    {"name": "page_load", "status": "pass", "screenshot": "01-landing.png"},
    {"name": "tab_aap2_login", "status": "pass", "screenshot": "20-tab-aap2-login.png"}
  ],
  "summary": {"total": 26, "passed": 26, "failed": 0}
}
```

**HTML report** at `{output-dir}/report.html` with embedded screenshots.

Exit code: 0 = all pass, 1 = any failure.

## Adding New Variants

Use Webwright's `/webwright:craft` command to generate a script for a new showroom type. See the design spec at `docs/superpowers/specs/2026-05-24-webwright-showroom-qa-design.md` for the variant detection approach.
