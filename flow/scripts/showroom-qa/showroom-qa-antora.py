#!/usr/bin/env python3
"""Playwright QA script for Antora-based RHDP showrooms.

Performs four-phase verification: page load, content, module walkthrough,
and service tab checks. Outputs a JSON report to stdout.
"""

import argparse
import base64
import json
import os
import re
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

VIEWPORT = {"width": 1280, "height": 800}
NAV_TIMEOUT = 30_000
IFRAME_TIMEOUT = 15_000
LOGIN_TIMEOUT = 10_000
ALL_PHASES = ["page_load", "content", "modules", "tabs"]
ALL_LEVELS = ["simple", "login", "state", "full"]


def parse_args():
    p = argparse.ArgumentParser(
        description="QA check for Antora-based RHDP showrooms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        examples:
          # Basic QA -- page load, content, modules, tabs:
          python3 showroom-qa-antora.py --url https://showroom-...

          # Verify login works on gated service tabs:
          python3 showroom-qa-antora.py --url https://showroom-... --level login

          # Deep state checks after login (pre-event validation):
          python3 showroom-qa-antora.py --url https://showroom-... --level state

          # Watch the browser work (headed mode):
          python3 showroom-qa-antora.py --url https://showroom-... --level login --headed

          # Only check tabs, skip HTML report:
          python3 showroom-qa-antora.py --url https://showroom-... --checks tabs --no-html

        levels:
          simple   Page load, content, modules, tab iframe checks (default)
          login    + Submit credentials to login-gated service tabs
          state    + Verify post-login content (populated dashboards, no errors)
          full     Reserved (not yet implemented)
        """))
    p.add_argument("--url", required=True, help="Showroom URL")
    p.add_argument("--user", default=None,
                   help="Login username (auto-extracted from page if not provided)")
    p.add_argument("--pass", dest="password", default=None,
                   help="Login password (auto-extracted from page if not provided)")
    p.add_argument("--level", default="simple", choices=ALL_LEVELS,
                   help="QA depth: simple (default), login, state, full")
    p.add_argument("--output-dir", default="./showroom-qa-results",
                   help="Screenshot output directory (default: ./showroom-qa-results)")
    p.add_argument("--checks", default=",".join(ALL_PHASES),
                   help="Comma-separated phases: page_load,content,modules,tabs")
    p.add_argument("--headed", action="store_true",
                   help="Run browser in headed mode (visible window)")
    p.add_argument("--no-html", action="store_true",
                   help="Skip HTML report generation")
    return p.parse_args()


def screenshot(page, output_dir, name):
    path = os.path.join(output_dir, name)
    page.screenshot(path=path)
    return name


def make_check(name, status, **extra):
    entry = {"name": name, "status": status}
    entry.update(extra)
    return entry


def _is_content_frame_url(url):
    """Check if a frame URL matches known Antora content iframe patterns."""
    return "/modules/" in url or url.endswith("/content")


def get_content_frame(page):
    """Find the Antora content frame via page.frames.

    Matches known URL patterns first (/www/modules/, /content), then
    falls back to finding the iframe with id="doc".
    """
    for frame in page.frames:
        if frame == page.main_frame:
            continue
        if _is_content_frame_url(frame.url):
            return frame

    try:
        doc_iframe = page.locator("iframe#doc")
        if doc_iframe.count() > 0:
            src = doc_iframe.get_attribute("src") or ""
            for frame in page.frames:
                if frame == page.main_frame:
                    continue
                if src and src in frame.url:
                    return frame
    except Exception:
        pass

    return None


def get_service_frames(page):
    """Return all frames that are NOT the main page or content frame.

    These are the cross-origin service iframes (AAP, Kira, etc.).
    """
    services = []
    content_frame = get_content_frame(page)
    for frame in page.frames:
        if frame == page.main_frame:
            continue
        if frame == content_frame:
            continue
        services.append(frame)
    return services


def open_sidebar(content_frame):
    """Click the hamburger menu button to reveal the sidebar navigation."""
    for selector in ["button.nav-toggle", "button[aria-label*='nav']",
                     "nav button"]:
        try:
            btn = content_frame.locator(selector).first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(0.5)
                return True
        except Exception:
            continue
    return False


def collect_module_links(content_frame):
    """Extract module links from the Antora sidebar or footer navigation."""
    modules = []

    open_sidebar(content_frame)

    for selector in [".nav-list a", ".nav-menu a", "nav.nav a",
                     ".navigation a"]:
        try:
            links = content_frame.locator(selector).all()
            for link in links:
                text = (link.text_content() or "").strip()
                href = link.get_attribute("href")
                if text and href and len(text) > 3 and not href.startswith("#"):
                    modules.append({"text": text, "href": href})
            if modules:
                return modules
        except Exception:
            continue

    # Fallback: scan article and footer for module links
    try:
        links = content_frame.locator("article a, nav a").all()
        seen = set()
        for link in links:
            text = (link.text_content() or "").strip()
            href = link.get_attribute("href")
            if (text and href and len(text) > 3
                    and href.endswith(".html")
                    and not href.startswith("#")
                    and href not in seen
                    and "module" in text.lower()):
                modules.append({"text": text, "href": href})
                seen.add(href)
    except Exception:
        pass

    return modules


def collect_progress_modules(page):
    """Fallback: extract module list from the outer-page Progress dialog."""
    modules = []
    try:
        progress_btn = page.locator("text=Progress").first
        if not progress_btn.is_visible(timeout=2000):
            return modules
        progress_btn.click()
        time.sleep(1)

        dialog = page.locator("dialog, [role='dialog']").first
        if not dialog.is_visible(timeout=3000):
            return modules

        items = dialog.locator("li").all()
        for item in items:
            text = (item.text_content() or "").strip()
            if text and len(text) > 3:
                modules.append({"text": text, "href": None})

        for selector in ["button:has-text('Close')", "button[aria-label='Close']"]:
            try:
                close_btn = page.locator(selector).first
                if close_btn.is_visible(timeout=1000):
                    close_btn.click()
                    time.sleep(0.5)
                    break
            except Exception:
                continue
    except Exception:
        pass
    return modules


def phase_page_load(page, url, output_dir):
    checks = []
    try:
        response = page.goto(url, wait_until="domcontentloaded",
                             timeout=NAV_TIMEOUT)
        status_code = response.status if response else 0

        if status_code == 200:
            page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT)
            title = page.title() or ""
            ss = screenshot(page, output_dir, "01-landing.png")
            checks.append(make_check("page_load", "pass",
                                     title=title, screenshot=ss))
        else:
            checks.append(make_check("page_load", "fail",
                                     error=f"HTTP {status_code}"))
    except PlaywrightTimeout:
        checks.append(make_check("page_load", "fail",
                                 error="Page load timed out"))
    except Exception as e:
        checks.append(make_check("page_load", "fail", error=str(e)))
    return checks


def extract_credentials(text):
    """Parse username and password from showroom page text."""
    username = None
    password = None

    for pattern in [r"[Uu]sername:\s*(\S+)", r"[Uu]ser:\s*(\S+)",
                    r"\b(user-[a-z0-9]+)\b"]:
        m = re.search(pattern, text)
        if m:
            username = m.group(1)
            break

    for pattern in [r"[Pp]assword:\s*(\S+)", r"[Pp]ass:\s*(\S+)"]:
        m = re.search(pattern, text)
        if m:
            password = m.group(1)
            break

    return username, password


def phase_content(page, output_dir):
    checks = []
    extracted_creds = (None, None)
    cf = get_content_frame(page)

    if not cf:
        checks.append(make_check("content_iframe", "fail",
                                 error="Content iframe not found"))
        return checks, extracted_creds

    checks.append(make_check("content_iframe", "pass"))

    try:
        cf.wait_for_load_state("domcontentloaded", timeout=IFRAME_TIMEOUT)
    except PlaywrightTimeout:
        checks.append(make_check("content_load", "fail",
                                 error="Content iframe timed out"))
        return checks, extracted_creds

    # Module list -- try sidebar nav first, fall back to Progress dialog
    modules = collect_module_links(cf)
    module_source = "sidebar"
    if not modules:
        modules = collect_progress_modules(page)
        module_source = "progress"
    if modules:
        checks.append(make_check("module_list", "pass",
                                 module_count=len(modules),
                                 module_source=module_source,
                                 modules=[m["text"] for m in modules]))
    else:
        checks.append(make_check("module_list", "pass",
                                 module_count=0,
                                 module_source="none",
                                 detail="Single-page showroom (no module navigation)"))

    # Credentials box -- extract actual values if present
    creds_found = False
    try:
        body_text = cf.locator("article").first.text_content(timeout=5000) or ""
        body_lower = body_text.lower()
        has_user = ("username" in body_lower or "user-" in body_lower
                    or "user:" in body_lower)
        if has_user and "password" in body_lower:
            creds_found = True
            extracted_creds = extract_credentials(body_text)
    except Exception:
        pass

    if creds_found:
        checks.append(make_check("credentials_box", "pass"))
    else:
        checks.append(make_check("credentials_box", "pass",
                                 detail="No credentials on landing page. "
                                        "Use --user and --pass if login "
                                        "checks are needed."))

    ss = screenshot(page, output_dir, "02-content.png")
    checks[-1]["screenshot"] = ss
    return checks, extracted_creds


def phase_modules(page, output_dir):
    checks = []
    cf = get_content_frame(page)
    if not cf:
        checks.append(make_check("modules_skip", "fail",
                                 error="Content iframe not found"))
        return checks

    modules = collect_module_links(cf)
    if not modules:
        progress_modules = collect_progress_modules(page)
        if progress_modules:
            h1 = None
            body_text = ""
            try:
                h1_el = cf.locator("h1").first
                if h1_el.is_visible(timeout=3000):
                    h1 = h1_el.text_content().strip()
            except Exception:
                pass
            for sel in ["article", "main", ".body", "body"]:
                try:
                    el = cf.locator(sel).first
                    if el.is_visible(timeout=2000):
                        body_text = el.text_content().strip()
                        if len(body_text) > 50:
                            break
                except Exception:
                    continue

            ss = screenshot(page, output_dir, "03-module-current.png")
            if len(body_text) > 50:
                checks.append(make_check(
                    "module_current_content", "pass",
                    title=h1 or "(no heading)",
                    screenshot=ss,
                    detail=f"{len(progress_modules)} modules in progress menu"))
            else:
                checks.append(make_check(
                    "module_current_content", "fail", screenshot=ss,
                    error="Current module page has no content"))
            return checks

        h1 = None
        body_text = ""
        try:
            h1_el = cf.locator("h1").first
            if h1_el.is_visible(timeout=3000):
                h1 = h1_el.text_content().strip()
        except Exception:
            pass
        for sel in ["article", "main", ".body", "body"]:
            try:
                el = cf.locator(sel).first
                if el.is_visible(timeout=2000):
                    body_text = el.text_content().strip()
                    if len(body_text) > 50:
                        break
            except Exception:
                continue
        ss = screenshot(page, output_dir, "03-module-current.png")
        if len(body_text) > 50:
            checks.append(make_check(
                "module_current_content", "pass",
                title=h1 or "(no heading)", screenshot=ss,
                detail="Single-page showroom"))
        else:
            checks.append(make_check(
                "module_current_content", "fail", screenshot=ss,
                error="No module navigation and current page has no content"))
        return checks

    for i, mod in enumerate(modules):
        check_name = f"module_{i + 1}_content"
        try:
            href = mod["href"]
            if not href.startswith("http"):
                base = cf.url.rsplit("/", 1)[0] + "/"
                href = base + href

            cf.goto(href, wait_until="domcontentloaded",
                    timeout=IFRAME_TIMEOUT)
            cf.wait_for_load_state("networkidle", timeout=IFRAME_TIMEOUT)

            h1 = None
            try:
                h1_el = cf.locator("h1").first
                if h1_el.is_visible(timeout=3000):
                    h1 = h1_el.text_content().strip()
            except Exception:
                pass

            body_text = ""
            try:
                article = cf.locator("article").first
                if article.is_visible(timeout=2000):
                    body_text = article.text_content().strip()
            except Exception:
                pass

            ss_name = f"{i + 3:02d}-module-{i + 1}.png"
            ss = screenshot(page, output_dir, ss_name)

            if h1 and len(body_text) > 50:
                checks.append(make_check(check_name, "pass",
                                         title=h1, screenshot=ss))
            elif not h1 and len(body_text) > 50:
                checks.append(make_check(check_name, "pass",
                                         title="(no heading)",
                                         screenshot=ss))
            else:
                checks.append(make_check(check_name, "fail",
                                         error="Page has no heading and "
                                               "insufficient content",
                                         screenshot=ss))

        except PlaywrightTimeout:
            checks.append(make_check(check_name, "fail",
                                     error=f"Timed out: {mod['text']}"))
        except Exception as e:
            checks.append(make_check(check_name, "fail", error=str(e)))

    return checks


LOGIN_SELECTORS = {
    "oauth": {
        "username": ["#inputUsername", "input[name='username']"],
        "password": ["#inputPassword", "input[name='password']"],
        "submit": [".btn-lg[type='submit']", "button[type='submit']"],
    },
    "rocket": {
        "username": ["input[name='emailOrUsername']", "#emailOrUsername",
                     "input[placeholder*='example']", "input[type='text']",
                     "input[type='email']"],
        "password": ["input[name='pass']", "input[type='password']"],
        "submit": ["button[type='submit']", "button.login",
                   "button:has-text('Login')"],
    },
    "langfuse": {
        "username": ["input[name='email']", "input[type='email']"],
        "password": ["input[name='password']", "input[type='password']"],
        "submit": ["button[type='submit']"],
    },
    "gitea": {
        "username": ["#user_name", "input[name='user_name']"],
        "password": ["#password", "input[name='password']"],
        "submit": ["button[type='submit']", "button.signin"],
    },
    "_default": {
        "username": ["input[name='username']", "input[name='user']",
                     "input[type='text']", "input[type='email']"],
        "password": ["input[name='password']", "input[type='password']"],
        "submit": ["button[type='submit']", "input[type='submit']",
                   "form button"],
    },
}


def _find_and_fill(frame, selectors, value, timeout=3000):
    for selector in selectors:
        try:
            el = frame.locator(selector).first
            if el.is_visible(timeout=timeout):
                el.fill(value)
                return True
        except Exception:
            continue
    return False


def _find_and_click(frame, selectors, timeout=3000):
    for selector in selectors:
        try:
            el = frame.locator(selector).first
            if el.is_visible(timeout=timeout):
                el.click()
                return True
        except Exception:
            continue
    return False


def _match_selector_set(frame_url):
    url_lower = frame_url.lower()
    for key, sels in LOGIN_SELECTORS.items():
        if key != "_default" and key in url_lower:
            return sels
    return LOGIN_SELECTORS["_default"]


def submit_login(frame, username, password):
    """Fill and submit a login form in a service iframe."""
    sels = _match_selector_set(frame.url)

    if not _find_and_fill(frame, sels["username"], username):
        return {"success": False,
                "error": "Could not locate username field. "
                         "Try --headed to inspect the login form."}

    if not _find_and_fill(frame, sels["password"], password):
        return {"success": False,
                "error": "Could not locate password field. "
                         "Try --headed to inspect the login form."}

    if not _find_and_click(frame, sels["submit"]):
        return {"success": False,
                "error": "Could not locate submit button. "
                         "Try --headed to inspect the login form."}

    try:
        frame.wait_for_load_state("networkidle", timeout=LOGIN_TIMEOUT)
    except PlaywrightTimeout:
        pass

    time.sleep(2)

    if has_login_gate(frame):
        return {"success": False,
                "error": "Login form still present after submission. "
                         "Credentials may be incorrect."}

    return {"success": True, "error": None}


def has_login_gate(frame):
    """Check whether a service frame presents a login form."""
    try:
        for selector in ["input[type='password']", "form[action*='login']",
                         "input[name='password']"]:
            if frame.locator(selector).count() > 0:
                return True
    except Exception:
        pass
    return False


def verify_post_login_state(frame, safe_label):
    """Smoke-test the post-login page for meaningful content."""
    ERROR_STRINGS = ["404", "not found", "forbidden", "unauthorized",
                     "internal server error", "502 bad gateway",
                     "503 service unavailable"]

    try:
        frame.wait_for_load_state("networkidle", timeout=LOGIN_TIMEOUT)
    except PlaywrightTimeout:
        pass

    try:
        body_text = frame.locator("body").first.text_content(timeout=5000) or ""
    except Exception:
        return {"status": "fail",
                "error": "Could not read page content after login"}

    text_len = len(body_text.strip())
    if text_len < 100:
        return {"status": "fail",
                "error": f"Page has very little content ({text_len} chars). "
                         "Dashboard may be empty or failed to render."}

    body_lower = body_text.lower()
    for err in ERROR_STRINGS:
        if err in body_lower:
            for selector in ["h1", "h2", "[role='alert']", ".alert",
                             ".pf-v5-c-alert"]:
                try:
                    els = frame.locator(selector).all()
                    for el in els:
                        el_text = (el.text_content() or "").lower()
                        if err in el_text:
                            return {"status": "fail",
                                    "error": f"Error indicator found: "
                                             f"'{el_text.strip()[:80]}'"}
                except Exception:
                    continue

    counts = {}
    for name, selector in [("tables", "table"),
                           ("lists", "ul, ol"),
                           ("cards", "[class*='card']"),
                           ("links", "a[href]")]:
        try:
            counts[name] = frame.locator(selector).count()
        except Exception:
            counts[name] = 0

    is_terminal = False
    for selector in [".xterm", ".terminal", "canvas", "textarea"]:
        try:
            if frame.locator(selector).count() > 0:
                is_terminal = True
                break
        except Exception:
            continue

    if is_terminal:
        return {"status": "pass",
                "content_summary": "Terminal session active"}

    parts = [f"{v} {k}" for k, v in counts.items() if v > 0]
    summary = ", ".join(parts) if parts else "content loaded"

    return {"status": "pass", "content_summary": f"Dashboard: {summary}"}


def phase_tabs(page, output_dir, username=None, password=None,
               level="simple"):
    checks = []

    try:
        tab_elements = page.locator("[role='tab']").all()
    except Exception:
        tab_elements = []

    if not tab_elements:
        checks.append(make_check("tabs_discovery", "pass",
                                 detail="No service tabs in this showroom"))
        return checks

    service_frames = get_service_frames(page)

    for i, tab_el in enumerate(tab_elements):
        label = (tab_el.text_content() or "").strip()
        if not label:
            continue

        safe_label = (label.lower()
                      .replace(" ", "_")
                      .replace("/", "_")
                      .replace(".", "_"))
        load_check = f"tab_{safe_label}_load"

        try:
            tab_el.click(timeout=5000)
            time.sleep(2)

            iframe_loaded = False
            login_detected = False
            sf = None

            if i < len(service_frames):
                try:
                    sf = service_frames[i]
                    sf.wait_for_load_state("domcontentloaded", timeout=5000)

                    if has_login_gate(sf):
                        login_detected = True

                    body_text = sf.locator("body").first.text_content(
                        timeout=3000) or ""
                    if len(body_text.strip()) > 5:
                        iframe_loaded = True
                except Exception:
                    pass

            ss_name = f"{20 + i:02d}-tab-{safe_label}.png"
            ss = screenshot(page, output_dir, ss_name)

            if iframe_loaded:
                checks.append(make_check(load_check, "pass",
                                         label=label, screenshot=ss))
            else:
                checks.append(make_check(load_check, "fail",
                                         label=label, screenshot=ss,
                                         error="Tab iframe blank or not loaded"))

            if not login_detected:
                continue

            if level == "simple":
                continue

            # -- login level and above --
            login_check = f"tab_{safe_label}_login"
            if not username or not password:
                checks.append(make_check(
                    login_check, "fail", label=label,
                    error="Login gate detected but no credentials available. "
                          "Provide --user and --pass, or ensure the showroom "
                          "landing page contains credentials."))
                continue

            result = submit_login(sf, username, password)
            login_ss_name = f"{20 + i:02d}-tab-{safe_label}-login.png"
            login_ss = screenshot(page, output_dir, login_ss_name)

            if result["success"]:
                checks.append(make_check(login_check, "pass",
                                         label=label, screenshot=login_ss))
            else:
                checks.append(make_check(login_check, "fail",
                                         label=label, screenshot=login_ss,
                                         error=result["error"]))
                continue

            if level != "state":
                continue

            # -- state level --
            state_check = f"tab_{safe_label}_state"
            state_result = verify_post_login_state(sf, safe_label)
            state_ss_name = f"{20 + i:02d}-tab-{safe_label}-state.png"
            state_ss = screenshot(page, output_dir, state_ss_name)

            checks.append(make_check(
                state_check, state_result["status"],
                label=label, screenshot=state_ss,
                content_summary=state_result.get("content_summary", ""),
                **({} if state_result["status"] == "pass"
                   else {"error": state_result.get("error", "")})))

        except PlaywrightTimeout:
            checks.append(make_check(load_check, "fail", label=label,
                                     error="Timed out clicking tab"))
        except Exception as e:
            checks.append(make_check(load_check, "fail", label=label,
                                     error=str(e)))

    return checks


def main():
    args = parse_args()
    output_dir = args.output_dir
    phases = [p.strip() for p in args.checks.split(",")]

    if args.level == "full":
        print("Full instruction execution is not yet implemented.",
              file=sys.stderr)
        print("Use --level state for the deepest available QA.",
              file=sys.stderr)
        sys.exit(0)

    for phase in phases:
        if phase not in ALL_PHASES:
            print(f"Unknown check phase: {phase}", file=sys.stderr)
            print(f"Valid phases: {', '.join(ALL_PHASES)}", file=sys.stderr)
            sys.exit(2)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    all_checks = []

    username = args.user
    password = args.password

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        context = browser.new_context(
            viewport=VIEWPORT,
            ignore_https_errors=True,
        )
        page = context.new_page()

        if "page_load" in phases:
            all_checks.extend(phase_page_load(page, args.url, output_dir))
            if any(c["status"] == "fail" and c["name"] == "page_load"
                   for c in all_checks):
                browser.close()
                print(json.dumps(build_report(args.url, all_checks,
                                              level=args.level)))
                sys.exit(1)

        if "content" in phases:
            content_checks, extracted_creds = phase_content(page, output_dir)
            all_checks.extend(content_checks)
            if not username and extracted_creds[0]:
                username = extracted_creds[0]
            if not password and extracted_creds[1]:
                password = extracted_creds[1]

        if "modules" in phases:
            all_checks.extend(phase_modules(page, output_dir))

        if "tabs" in phases:
            all_checks.extend(phase_tabs(page, output_dir,
                                         username=username,
                                         password=password,
                                         level=args.level))

        browser.close()

    report = build_report(args.url, all_checks, level=args.level)
    print(json.dumps(report))

    if not args.no_html:
        generate_html_report(report, output_dir)

    passed = report["summary"]["passed"]
    total = report["summary"]["total"]
    print(f"QA complete: {passed}/{total} checks passed (level={args.level})",
          file=sys.stderr)
    sys.exit(1 if report["summary"]["failed"] > 0 else 0)


HTML_CSS = """\
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
       sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem;
       color: #333; background: #fafafa; }
.banner { padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; }
.banner.pass { background: #d4edda; border: 1px solid #28a745; }
.banner.fail { background: #f8d7da; border: 1px solid #dc3545; }
.banner h1 { margin: 0 0 0.5rem 0; font-size: 1.4rem; }
.banner .meta { font-size: 0.85rem; color: #555; }
.banner .counts { font-size: 1.1rem; margin-top: 0.5rem; }
.check { border: 1px solid #ddd; border-radius: 6px; margin-bottom: 0.5rem;
         background: #fff; }
.check-header { padding: 0.75rem 1rem; display: flex; align-items: center;
                gap: 0.75rem; }
.check-header .icon { font-size: 1.2rem; flex-shrink: 0; }
.check-header .name { font-weight: 600; font-family: monospace; }
.check-header .detail { color: #666; font-size: 0.85rem; margin-left: auto; }
.check.fail .check-header { background: #fff5f5; }
.check.pass .check-header { background: #f0fff0; }
.error { color: #dc3545; font-size: 0.85rem; padding: 0 1rem 0.75rem 2.75rem; }
details { padding: 0.5rem 1rem; }
details summary { cursor: pointer; font-size: 0.85rem; color: #007bff; }
details img { max-width: 100%; margin-top: 0.5rem; border: 1px solid #ddd;
              border-radius: 4px; }
"""


def generate_html_report(report, output_dir):
    passed = report["summary"]["passed"]
    total = report["summary"]["total"]
    failed = total - passed
    status_class = "pass" if failed == 0 else "fail"
    status_text = "ALL CHECKS PASSED" if failed == 0 else f"{failed} CHECK(S) FAILED"
    level = report.get("level", "simple")

    checks_html = []
    for check in report["checks"]:
        cls = check["status"]
        icon = "&#x2705;" if cls == "pass" else "&#x274c;"
        name = check["name"]

        detail_parts = []
        if check.get("title"):
            detail_parts.append(check["title"])
        if check.get("label"):
            detail_parts.append(check["label"])
        if check.get("module_count"):
            detail_parts.append(f"{check['module_count']} modules")
        if check.get("content_summary"):
            detail_parts.append(check["content_summary"])
        detail = " | ".join(detail_parts)

        error_html = ""
        if check.get("error"):
            error_html = (f'<div class="error">{check["error"]}</div>')

        screenshot_html = ""
        ss = check.get("screenshot")
        if ss:
            ss_path = os.path.join(output_dir, ss)
            if os.path.exists(ss_path):
                with open(ss_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                screenshot_html = (
                    f'<details><summary>View screenshot</summary>'
                    f'<img src="data:image/png;base64,{b64}" '
                    f'alt="{name}"/></details>')

        checks_html.append(
            f'<div class="check {cls}">'
            f'<div class="check-header">'
            f'<span class="icon">{icon}</span>'
            f'<span class="name">{name}</span>'
            f'<span class="detail">{detail}</span>'
            f'</div>'
            f'{error_html}'
            f'{screenshot_html}'
            f'</div>')

    html = (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<title>Showroom QA Report</title>'
        f'<style>{HTML_CSS}</style></head><body>'
        f'<div class="banner {status_class}">'
        f'<h1>Showroom QA Report</h1>'
        f'<div class="meta">'
        f'URL: {report["url"]}<br>'
        f'Variant: {report["variant"]} | Level: {level}<br>'
        f'Time: {report["timestamp"]}'
        f'</div>'
        f'<div class="counts">'
        f'{status_text} &mdash; {passed}/{total} passed'
        f'</div></div>'
        f'{"".join(checks_html)}'
        f'</body></html>')

    report_path = os.path.join(output_dir, "report.html")
    with open(report_path, "w") as f:
        f.write(html)
    print(f"HTML report: {report_path}", file=sys.stderr)


def build_report(url, checks, level="simple"):
    total = len(checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "url": url,
        "variant": "antora",
        "level": level,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "summary": {"total": total, "passed": passed,
                     "failed": total - passed},
    }


if __name__ == "__main__":
    main()
