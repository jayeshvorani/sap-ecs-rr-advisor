#!/Users/I553472/Documents/Claude_Code_Projects/.venv/bin/python3
# ---------------------------------------------------------------------------
# IMPORTANT FOR OTHER USERS:
# The shebang above is hardcoded for the repo author's environment.
# If you are cloning this repository, update the shebang to match your
# own Python virtual environment path. For example:
#   #!/usr/bin/env python3
#   #!/home/yourname/myproject/.venv/bin/python3
# See docs/setup-claude-code.md → Step 3 for full setup instructions.
# ---------------------------------------------------------------------------
"""
setup.py — SAP ECS R&R Advisor one-time setup script.

Downloads all active PDFs from SAP, extracts version strings,
updates registry.json and status.json with results.

Usage:
    python3 setup.py

Run once after cloning. Already-downloaded files are not skipped —
this script always re-downloads. Use refresh.py for incremental updates.
"""

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.resolve()
REGISTRY_FILE = REPO_ROOT / "registry.json"
STATUS_FILE = REPO_ROOT / "status.json"
LOGS_DIR = REPO_ROOT / "logs"
LOG_FILE = LOGS_DIR / "setup.log"
PDFS_DIR = REPO_ROOT / "pdfs"
PDFTOTEXT = "/opt/homebrew/bin/pdftotext"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/pdf,application/octet-stream,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.sap.com/about/agreements/policies/hec-services.html",
}

SAP_POLICY_URL = "https://www.sap.com/about/agreements/policies/hec-services.html"

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_display() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path: Path, data: dict) -> None:
    """Write JSON atomically: write to temp file, then rename."""
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def extract_version(pdf_path: Path) -> str | None:
    """
    Extract version string from the first 3 pages of a PDF using pdftotext.
    Searches for patterns like: v.03.2026, enGlobal.v.X, v3-2026, ENGLISH vX
    Returns the first match found, or None.
    """
    try:
        result = subprocess.run(
            [PDFTOTEXT, "-f", "1", "-l", "3", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        text = result.stdout
        patterns = [
            r"v\.\d+\.\d{4}[a-z]?",          # v.03.2026
            r"enGlobal\.v\.\S+",               # enGlobal.v.X
            r"v\d+-\d{4}[a-z]?",               # v3-2026, v3-2026a
            r"ENGLISH\s+v\S+",                 # ENGLISH v3-2026
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return m.group(0).strip()
    except Exception as e:
        log.warning("version extraction failed for %s: %s", pdf_path.name, e)
    return None


def print_error_block(model: dict, reason: str) -> None:
    sn = model["short_name"]
    fn = model["full_name"]
    lf = model["local_file"]
    url = model["url"]
    print(f"""
   \u274c FAILED: {sn}
   \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
   File    : {lf}
   URL     : {url}
   Reason  : {reason}

   What to do:
   1. Visit: https://www.sap.com/about/agreements/policies/hec-services.html
   2. Find the current URL for "{fn}"
   3. Update registry.json — change the "url" field for {sn}
   4. Run setup.py again (failed models will be retried)

   \u26a0\ufe0f  This model will show a warning in all Claude responses
       until resolved. See docs/troubleshooting.md for help.
   \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500""")


def check_environment() -> bool:
    """Validate environment. Returns True if all checks pass."""
    print("\n\U0001f50d Environment check...")
    ok = True

    # Check pdftotext
    if os.path.isfile(PDFTOTEXT) and os.access(PDFTOTEXT, os.X_OK):
        print(f"   \u2705 pdftotext found: {PDFTOTEXT}")
    else:
        print(f"   \u274c pdftotext not found at {PDFTOTEXT}")
        print("      Install with: brew install poppler")
        ok = False

    # Check requests
    try:
        import requests  # noqa: F401
        print("   \u2705 requests library available")
    except ImportError:
        print("   \u274c requests not installed")
        print("      Install with: pip install requests")
        ok = False

    # Check / create pdfs/ directory
    PDFS_DIR.mkdir(exist_ok=True)
    print(f"   \u2705 pdfs/ directory ready: {PDFS_DIR}")

    # Check registry
    if REGISTRY_FILE.exists():
        print(f"   \u2705 registry.json found: {REGISTRY_FILE}")
    else:
        print(f"   \u274c registry.json missing: {REGISTRY_FILE}")
        ok = False

    return ok


# ---------------------------------------------------------------------------
# Core download logic
# ---------------------------------------------------------------------------
def download_pdf(url: str, dest_path: Path, short_name: str) -> bool:
    """
    Download a PDF from `url` to a temp file, then atomically move it to
    `dest_path`. Implements a 3-step retry strategy to handle 403 responses:

      Step 1 — Simple User-Agent header only
      Step 2 (on 403) — Full browser headers, 2 s wait
      Step 3 (on 403) — Session + cookie warm-up via SAP policy page, 3 s wait

    Returns True if any attempt succeeds, False if all three fail.
    Temp files are always cleaned up on failure.
    """
    import requests
    from requests.exceptions import RequestException

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None

    def _stream_to_temp(response) -> Path:
        """Write a streaming response to a temp file; return its Path."""
        with tempfile.NamedTemporaryFile(
            dir=dest_path.parent, suffix=".tmp", delete=False
        ) as tmp:
            path = Path(tmp.name)
            for chunk in response.iter_content(chunk_size=65536):
                tmp.write(chunk)
        return path

    # ------------------------------------------------------------------
    # Attempt 1 — minimal User-Agent header
    # ------------------------------------------------------------------
    print(f"  \u21bb Attempt 1/3 for {short_name}...")
    log.info("%s | attempt 1/3 | minimal UA", short_name)
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=60,
            stream=True,
        )
        if resp.status_code == 200:
            tmp_path = _stream_to_temp(resp)
            tmp_path.replace(dest_path)
            log.info("%s | attempt 1 succeeded", short_name)
            return True
        if resp.status_code != 403:
            # Non-403 failure — no point retrying with different headers
            log.error("%s | attempt 1 | HTTP %s — not retrying", short_name, resp.status_code)
            return False
        log.info("%s | attempt 1 | HTTP 403 — retrying with full headers", short_name)
    except RequestException as e:
        log.error("%s | attempt 1 | network error: %s", short_name, e)
        return False

    # ------------------------------------------------------------------
    # Attempt 2 — full browser headers, 2 s wait
    # ------------------------------------------------------------------
    time.sleep(2)
    print(f"  \u21bb Attempt 2/3 for {short_name} (full browser headers)...")
    log.info("%s | attempt 2/3 | full browser headers", short_name)
    try:
        resp = requests.get(
            url,
            headers=BROWSER_HEADERS,
            timeout=60,
            stream=True,
        )
        if resp.status_code == 200:
            tmp_path = _stream_to_temp(resp)
            tmp_path.replace(dest_path)
            log.info("%s | attempt 2 succeeded", short_name)
            return True
        if resp.status_code != 403:
            log.error("%s | attempt 2 | HTTP %s — not retrying", short_name, resp.status_code)
            return False
        log.info("%s | attempt 2 | HTTP 403 — retrying with session + cookies", short_name)
    except RequestException as e:
        log.error("%s | attempt 2 | network error: %s", short_name, e)
        return False

    # ------------------------------------------------------------------
    # Attempt 3 — session cookie warm-up via SAP policy page, 3 s wait
    # ------------------------------------------------------------------
    time.sleep(3)
    print(f"  \u21bb Attempt 3/3 for {short_name} (session + cookies)...")
    log.info("%s | attempt 3/3 | session warm-up via %s", short_name, SAP_POLICY_URL)
    try:
        session = requests.Session()
        session.get(SAP_POLICY_URL, headers=BROWSER_HEADERS, timeout=30)
        time.sleep(3)
        resp = session.get(url, headers=BROWSER_HEADERS, timeout=60, stream=True)
        if resp.status_code == 200:
            tmp_path = _stream_to_temp(resp)
            tmp_path.replace(dest_path)
            log.info("%s | attempt 3 succeeded", short_name)
            return True
        log.error("%s | attempt 3 | HTTP %s — all retries exhausted", short_name, resp.status_code)
    except RequestException as e:
        log.error("%s | attempt 3 | network error: %s", short_name, e)

    # Clean up any stray temp file
    if tmp_path and tmp_path.exists():
        tmp_path.unlink(missing_ok=True)

    print(f"  \u274c FAILED: {short_name} \u2014 all download attempts failed.")
    print(f"     See docs/troubleshooting.md \u2192 Manual PDF download fallback")
    return False


def download_model(model: dict, registry: dict, status: dict) -> bool:
    """
    Download a single model PDF using download_pdf().
    Updates registry and status in-place; saves both atomically after each model.
    Returns True on success, False on failure.
    """
    sn = model["short_name"]
    url = model["url"]
    local_file = REPO_ROOT / model["local_file"]
    now = now_iso()

    print(f"Downloading {sn}: {model['full_name']}...")

    # Update last_attempt immediately
    status["models"][sn]["last_attempt"] = now

    success = download_pdf(url, local_file, sn)

    if not success:
        reason = "HTTP 403 — all download attempts failed"
        print_error_block(model, reason)
        log.error("%s | FAILED | %s | %s", sn, reason, url)
        status["models"][sn].update({
            "status": "failed",
            "error": reason,
            "http_status": 403,
        })
        save_json_atomic(STATUS_FILE, status)
        return False

    # Extract version from downloaded file
    version = extract_version(local_file)

    # Update registry model entry
    for m in registry["models"]:
        if m["short_name"] == sn:
            m["document_version"] = version
            m["last_checked"] = now
            break

    # Update status
    status["models"][sn].update({
        "status": "ok",
        "last_success": now,
        "error": None,
        "http_status": 200,
    })

    version_display = version if version else "(unknown)"
    print(f"  \u2705 {sn} \u2014 Version: {version_display}")
    log.info("%s | OK | version=%s", sn, version_display)

    # Save both files atomically after each successful model
    save_json_atomic(REGISTRY_FILE, registry)
    save_json_atomic(STATUS_FILE, status)

    return True


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def print_summary(registry: dict, status: dict) -> None:
    models = registry["models"]
    col_model = max(len(m["short_name"]) for m in models) + 2
    col_status = 10
    col_version = max(
        len(m["document_version"] or "\u2014") for m in models
    ) + 2
    col_checked = 18

    def row(model_col, status_col, version_col, checked_col, sep="\u2502"):
        return (
            f"{sep} {model_col:<{col_model}}"
            f"{sep} {status_col:<{col_status}}"
            f"{sep} {version_col:<{col_version}}"
            f"{sep} {checked_col:<{col_checked}}{sep}"
        )

    top    = f"\u250c{'':}\u2500" + "\u2500" * col_model + "\u252c\u2500" + "\u2500" * col_status + "\u252c\u2500" + "\u2500" * col_version + "\u252c\u2500" + "\u2500" * col_checked + "\u2510"
    mid    = f"\u251c{'':}\u2500" + "\u2500" * col_model + "\u253c\u2500" + "\u2500" * col_status + "\u253c\u2500" + "\u2500" * col_version + "\u253c\u2500" + "\u2500" * col_checked + "\u2524"
    bot    = f"\u2514{'':}\u2500" + "\u2500" * col_model + "\u2534\u2500" + "\u2500" * col_status + "\u2534\u2500" + "\u2500" * col_version + "\u2534\u2500" + "\u2500" * col_checked + "\u2518"

    print(f"\n{'='*70}")
    print("DOWNLOAD SUMMARY")
    print(f"{'='*70}")
    print(top)
    print(row("Model", "Status", "Version", "Last Checked"))
    print(mid)

    for m in models:
        sn = m["short_name"]
        st = status["models"].get(sn, {})
        s = st.get("status", "pending")
        if s == "ok":
            status_str = "\u2705 OK"
        elif s == "failed":
            status_str = "\u274c FAIL"
        elif s == "skipped":
            status_str = "\u23ed SKIP"
        else:
            status_str = "\u23f3 PENDING"

        version_str = m.get("document_version") or "\u2014"
        checked_str = "\u2014"
        if m.get("last_checked"):
            try:
                dt = datetime.fromisoformat(m["last_checked"].replace("Z", "+00:00"))
                checked_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                checked_str = m["last_checked"][:16]

        print(row(sn, status_str, version_str, checked_str))

    print(bot)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    import requests  # validate import at entry

    print("\nSAP ECS R&R Advisor — Setup Script v1.0")
    print("=" * 70)

    if not check_environment():
        print("\n\u274c Environment check failed. Fix issues above and re-run.")
        return 1

    print(f"\n\U0001f4e5 Starting downloads... ({now_display()})\n")

    registry = load_json(REGISTRY_FILE)
    status = load_json(STATUS_FILE)

    # Ensure status has entries for all models
    for m in registry["models"]:
        sn = m["short_name"]
        if sn not in status["models"]:
            status["models"][sn] = {
                "status": "pending",
                "last_success": None,
                "last_attempt": None,
                "error": None,
                "http_status": None,
            }

    failures = []
    for model in registry["models"]:
        if not model.get("active", True):
            sn = model["short_name"]
            print(f"Skipping {sn} (active: false)")
            status["models"][sn]["status"] = "skipped"
            log.info("%s | SKIPPED | active=false", sn)
            save_json_atomic(STATUS_FILE, status)
            continue

        success = download_model(model, registry, status)
        if not success:
            failures.append(model["short_name"])

    # Record run result
    now = now_iso()
    status["last_run"] = now
    status["last_run_result"] = "ok" if not failures else "partial" if len(failures) < len(registry["models"]) else "failed"
    save_json_atomic(STATUS_FILE, status)
    save_json_atomic(REGISTRY_FILE, registry)

    print_summary(registry, status)

    if failures:
        n = len(failures)
        print(f"\n\u26a0\ufe0f  {n} model(s) failed: {', '.join(failures)}")
        print("   See details above.")
        print("   Run setup.py again after fixing the URLs in registry.json.")
        print("   Failed models will show warnings in all Claude responses")
        print("   until resolved.")
        log.error("Run complete | %d failure(s): %s", n, ", ".join(failures))
        return 1

    print(f"\n\u2705 All {len(registry['models'])} models downloaded successfully.")
    log.info("Run complete | all OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
