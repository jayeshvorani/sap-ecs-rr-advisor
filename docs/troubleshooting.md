# Troubleshooting

---

## PDF Download Failures

### HTTP 404 — URL has changed

**Symptom:** setup.py or refresh.py reports `HTTP 404` for a model.

**Cause:** SAP has updated the document and the PDF URL has changed. SAP publishes new versions of R&R documents annually (typically named `v3-2026`, `v3-2025`, etc.) and the old URL no longer works.

**Fix:**
1. Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Filter the page for "Roles and Responsibilities" and "English"
3. Find the document matching the `full_name` from registry.json
4. Right-click the PDF download link → Copy link address
5. Open `registry.json` and update the `"url"` field for the affected model
6. Run `python3 setup.py` again

---

### HTTP 403 — Access forbidden

**Symptom:** setup.py or refresh.py reports `HTTP 403` after all three retry attempts.

**Cause:** SAP's server is refusing the programmatic request. The scripts automatically retry with progressively more browser-like behaviour (full browser headers, then a session cookie warm-up via SAP's policy page). If all three attempts return 403, SAP's CDN is actively blocking non-browser access for that document at that time.

**What to do:**
1. Wait 10–15 minutes and run `python3 setup.py` again — CDN blocks are often temporary
2. If it still fails, use the **Manual PDF download fallback** below
3. If the URL in your browser also returns 403, the document may have been temporarily removed or restricted by SAP — wait 24 hours and retry
4. If the problem persists, open an issue at [https://github.com/jayeshvorani/sap-ecs-rr-advisor](https://github.com/jayeshvorani/sap-ecs-rr-advisor)

---

### Manual PDF download fallback

If all automated download attempts fail for a model (shown as `❌ FAILED: [short_name] — all download attempts failed`), download the PDF manually:

1. Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Search for the document name shown in `registry.json` under `"full_name"`
3. Download the PDF from your browser by clicking the download link
4. Rename the file to match the filename in `registry.json` under `"local_file"` — for example, `pce.pdf`
5. Place it in the `pdfs/` folder of this repository
6. Run the following command to extract and record the version:
   ```bash
   python3 refresh.py
   ```
   `refresh.py` will detect the file exists and update `registry.json` with the version string and `status.json` with `"status": "ok"`

After completing these steps, the model's warning will no longer appear in Claude's responses.

---

### Connection timeout

**Symptom:** setup.py or refresh.py hangs then reports a timeout error.

**Cause:** Network connectivity issue or SAP's servers are slow to respond.

**Fix:**
1. Check your internet connection
2. Try opening one of the PDF URLs in your browser to confirm SAP's site is reachable
3. Wait a few minutes and run the script again — transient network issues usually resolve quickly
4. If you are behind a corporate proxy or VPN, try disconnecting from it and retrying

---

### SSL certificate error

**Symptom:** Error message contains `SSL`, `certificate`, or `CERTIFICATE_VERIFY_FAILED`.

**Cause:** Your system's SSL certificates may be outdated or there may be a proxy intercepting the connection.

**Fix:**
```bash
# Update certificates on macOS
/Applications/Python\ 3.x/Install\ Certificates.command
# or:
pip install --upgrade certifi
```

If you are behind a corporate proxy that performs SSL inspection, contact your IT team — they may need to add the SAP certificate to your trusted store.

---

### How status.json reflects failures

When a download fails, `status.json` is updated immediately:

```json
"PCE": {
  "status": "failed",
  "last_success": "2026-01-15T08:00:00Z",
  "last_attempt": "2026-03-28T08:00:00Z",
  "error": "HTTP 404",
  "http_status": 404
}
```

- `status`: `"failed"` — shown as a warning in Claude
- `last_success`: last time the download worked — Claude uses the PDF from this date
- `error`: the specific error message

---

### How warnings appear in Claude responses

If a model has `"status": "failed"` in status.json, Claude will show this at the top of every answer for that model:

```
⚠️  PDF STATUS WARNING
This model's PDF failed on 2026-03-28T08:00:00Z (HTTP 404).
Response below is based on last successful version from 2026-01-15T08:00:00Z.
SAP may have published updates since then.
To resolve: docs/troubleshooting.md → PDF download failures
────────────────────────────────────────────────────────────
```

---

### Confirming a fix worked

After updating the URL and re-running setup.py:
1. Check the printed summary table — the model should show ✅ OK
2. Open `status.json` — the model should show `"status": "ok"` and `"error": null`
3. Start a new Claude Code session — the warning should no longer appear

---

## Claude Code Issues

### CLAUDE.md not loading

**Symptom:** Claude does not show the ready confirmation at session start.

**Fix:**
- Confirm CLAUDE.md exists in your working directory or a parent directory
- Claude Code loads CLAUDE.md files from the current directory upward to your home directory
- Run `ls -la` in your project root to confirm the file exists
- Check the file is not empty: `cat CLAUDE.md`

---

### Skill not recognising model

**Symptom:** Claude does not auto-select the correct model from your question.

**Fix:**
- Try using the exact `short_name` from registry.json in your question (e.g., "PCE", "HEC_ADV")
- If you typed a keyword that should trigger auto-select, check SKILL.md → Model Selection table for the supported triggers
- Type `models` to see the full list and select by number

---

### PDF not found error

**Symptom:** Claude says it cannot find or read the PDF file.

**Fix:**
- Run `ls pdfs/` in the repo directory to confirm the PDF was downloaded
- If missing, run `python3 setup.py` to download it
- Check `status.json` to confirm the model shows `"status": "ok"`

---

### Version shows as null

**Symptom:** Claude reports `⚠️ Version unknown` in the version header.

**Cause:** The PDF was downloaded but the version string could not be extracted, or setup.py was not run.

**Fix:**
1. Run `python3 setup.py` to download and extract versions
2. If the script ran but version is still null, `pdftotext` may not be installed or may not be at `/opt/homebrew/bin/pdftotext`
3. Verify: `/opt/homebrew/bin/pdftotext -v`
4. If missing, install: `brew install poppler`

---

## Claude Projects Issues

### PDF upload failing

**Symptom:** Claude Project rejects the PDF upload.

**Possible causes and fixes:**
- **File too large:** Claude Projects have per-file size limits. If a PDF exceeds the limit, check if the download was complete (open the file in a PDF viewer)
- **Wrong file format:** Confirm the file is a PDF by opening it — if it opens as a PDF, the format is correct
- **Upload timeout:** Try uploading one file at a time rather than all at once

---

### RAG mode activating

**Symptom:** Claude's answers seem to be searching/retrieving rather than reading the full document.

**What this means:** Claude Projects use retrieval-augmented generation (RAG) when documents are large. Claude retrieves relevant sections rather than reading the entire PDF.

**When it helps:** RAG is usually fine — Claude retrieves the relevant section for your question.

**When it hurts:** For broad questions ("summarise all SAP responsibilities") or cross-section comparisons, RAG may miss relevant sections. In these cases, ask more specific questions or break the query into multiple targeted questions.

---

### Project instructions not being followed

**Symptom:** Claude gives answers without version headers, section references, or confidence ratings.

**Fix:**
1. Open your Claude Project → Settings
2. Confirm the Project Instructions field contains the full content from `PROJECT_INSTRUCTIONS.md`
3. Start a **new chat** within the Project — do not continue an existing chat that was started before the instructions were set
4. If the issue persists, clear the instructions, save, re-paste, and save again

---

### PDF appears outdated

**Symptom:** Claude reports an old version in the version header that does not match the current SAP document.

**Fix:**
1. Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Download the latest version of the PDF
3. Open your Claude Project
4. Delete the old PDF from the knowledge base
5. Upload the new PDF
