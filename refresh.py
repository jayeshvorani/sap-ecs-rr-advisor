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
refresh.py — SAP ECS R&R Advisor incremental refresh script.

Like setup.py, but skips models where the local file exists AND the
version string has not changed. Only downloads if the file is missing
or the remote version differs from the locally recorded version.

Intended to run automatically via launchd every Sunday at 08:00.
Can also be run manually: python3 refresh.py

Trims log entries older than 30 days on each run.
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
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.resolve()
REGISTRY_FILE = REPO_ROOT / "registry.json"
STATUS_FILE = REPO_ROOT / "status.json"
LOGS_DIR = REPO_ROOT / "logs"
LOG_FILE = LOGS_DIR / "refresh.log"
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
# Helpers (shared with setup.py)
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
    """Extract version string from first 3 pages of a PDF."""
    try:
        result = subprocess.run(
            [PDFTOTEXT, "-f", "1", "-l", "3", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        text = result.stdout
        patterns = [
            r"v\.\d+\.\d{4}[a-z]?",
            r"enGlobal\.v\.\S+",
            r"v\d+-\d{4}[a-z]?",
            r"ENGLISH\s+v\S+",
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
   4. Run refresh.py again (already-downloaded files are skipped)

   \u26a0\ufe0f  This model will show a warning in all Claude responses
       until resolved. See docs/troubleshooting.md for help.
   \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500""")


# ---------------------------------------------------------------------------
# Shared download logic (identical to setup.py)
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


# ---------------------------------------------------------------------------
# Log trimming
# ---------------------------------------------------------------------------
def trim_log(log_path: Path, days: int = 30) -> None:
    """Remove log lines older than `days` days."""
    if not log_path.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    kept = []
    removed = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            # Lines start with ISO timestamp: 2026-03-28T08:00:00
            try:
                ts_str = line[:19]
                ts = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
                if ts >= cutoff:
                    kept.append(line)
                else:
                    removed += 1
            except (ValueError, IndexError):
                kept.append(line)  # keep unparseable lines
    if removed > 0:
        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(kept)
        log.info("Log trimmed: removed %d entries older than %d days", removed, days)


# ---------------------------------------------------------------------------
# Core refresh logic
# ---------------------------------------------------------------------------
def needs_refresh(model: dict) -> tuple[bool, str]:
    """
    Determine if a model needs downloading.
    Returns (should_download, reason_string).
    """
    local_file = REPO_ROOT / model["local_file"]

    # File doesn't exist
    if not local_file.exists():
        return True, "file missing"

    # No recorded version
    recorded_version = model.get("document_version")
    if not recorded_version:
        return True, "no version recorded"

    # Try to extract version from existing local file
    current_version = extract_version(local_file)
    if current_version and current_version == recorded_version:
        return False, f"CURRENT — version {recorded_version} unchanged"

    if current_version and current_version != recorded_version:
        return True, f"version changed: {recorded_version} → {current_version}"

    # Can't extract version from existing file — download to check
    return True, "version unverifiable — re-downloading to check"


def refresh_model(model: dict, registry: dict, status: dict) -> tuple[bool, bool]:
    """
    Refresh a single model if needed.
    Returns (success: bool, was_updated: bool).
    """
    sn = model["short_name"]
    url = model["url"]
    local_file = REPO_ROOT / model["local_file"]
    now = now_iso()

    should_download, reason = needs_refresh(model)

    if not should_download:
        print(f"  \u23ed {sn} — {reason}")
        log.info("%s | CURRENT | %s", sn, reason)
        return True, False

    print(f"Downloading {sn}: {model['full_name']}...")
    print(f"  Reason: {reason}")

    status["models"][sn]["last_attempt"] = now

    success = download_pdf(url, local_file, sn)

    if not success:
        reason_str = "HTTP 403 — all download attempts failed"
        print_error_block(model, reason_str)
        log.error("%s | FAILED | %s | %s", sn, reason_str, url)
        status["models"][sn].update({
            "status": "failed",
            "error": reason_str,
            "http_status": 403,
        })
        save_json_atomic(STATUS_FILE, status)
        return False, False

    # Extract version from new download
    new_version = extract_version(local_file)
    old_version = model.get("document_version")

    # Determine if this was an actual version update
    was_updated = (new_version != old_version) if new_version else True

    # Update registry
    for m in registry["models"]:
        if m["short_name"] == sn:
            m["document_version"] = new_version
            m["last_checked"] = now
            break

    status["models"][sn].update({
        "status": "ok",
        "last_success": now,
        "error": None,
        "http_status": 200,
    })

    version_display = new_version if new_version else "(unknown)"
    if was_updated and old_version:
        print(f"  \u2705 {sn} \u2014 Updated: {old_version} \u2192 {version_display}")
        log.info("%s | UPDATED | %s -> %s", sn, old_version, version_display)
    else:
        print(f"  \u2705 {sn} \u2014 Version: {version_display}")
        log.info("%s | OK | version=%s", sn, version_display)

    save_json_atomic(REGISTRY_FILE, registry)
    save_json_atomic(STATUS_FILE, status)

    return True, was_updated


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

    top = f"\u250c\u2500" + "\u2500" * col_model + "\u252c\u2500" + "\u2500" * col_status + "\u252c\u2500" + "\u2500" * col_version + "\u252c\u2500" + "\u2500" * col_checked + "\u2510"
    mid = f"\u251c\u2500" + "\u2500" * col_model + "\u253c\u2500" + "\u2500" * col_status + "\u253c\u2500" + "\u2500" * col_version + "\u253c\u2500" + "\u2500" * col_checked + "\u2524"
    bot = f"\u2514\u2500" + "\u2500" * col_model + "\u2534\u2500" + "\u2500" * col_status + "\u2534\u2500" + "\u2500" * col_version + "\u2534\u2500" + "\u2500" * col_checked + "\u2518"

    print(f"\n{'='*70}")
    print("REFRESH SUMMARY")
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

    print("\nSAP ECS R&R Advisor — Refresh Script v1.0")
    print("=" * 70)
    print(f"Started: {now_display()}")

    # Trim old log entries first
    trim_log(LOG_FILE, days=30)

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
    updated_models = []

    for model in registry["models"]:
        if not model.get("active", True):
            sn = model["short_name"]
            print(f"  Skipping {sn} (active: false)")
            status["models"][sn]["status"] = "skipped"
            log.info("%s | SKIPPED | active=false", sn)
            save_json_atomic(STATUS_FILE, status)
            continue

        success, was_updated = refresh_model(model, registry, status)
        if not success:
            failures.append(model["short_name"])
        elif was_updated:
            updated_models.append(model["short_name"])

    # Record run result
    now = now_iso()
    status["last_run"] = now
    status["last_run_result"] = (
        "ok" if not failures
        else "partial" if len(failures) < len(registry["models"])
        else "failed"
    )
    save_json_atomic(STATUS_FILE, status)
    save_json_atomic(REGISTRY_FILE, registry)

    print_summary(registry, status)

    if updated_models:
        print(f"\n\U0001f4c4 Updated models: {', '.join(updated_models)}")
        print("   Updated models require re-upload to Claude Projects.")
        print("   See docs/setup-web-projects.md \u2192 Keeping PDFs current.")

    if failures:
        n = len(failures)
        print(f"\n\u26a0\ufe0f  {n} model(s) failed: {', '.join(failures)}")
        print("   See details above.")
        print("   Run refresh.py again after fixing the URLs in registry.json.")
        print("   Failed models will show warnings in all Claude responses")
        print("   until resolved.")
        log.error("Run complete | %d failure(s): %s", n, ", ".join(failures))
        return 1

    if updated_models:
        print(f"\n\u2705 Refresh complete. {len(updated_models)} model(s) updated.")
    else:
        print("\n\u2705 Refresh complete. All models are current — no updates needed.")
    log.info("Run complete | %d updated | %d failures", len(updated_models), len(failures))
    return 0


if __name__ == "__main__":
    sys.exit(main())
