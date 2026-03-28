# Managing Model Changes

This guide explains how to maintain `registry.json` — adding new models, disabling old ones, updating URLs, and understanding how each field affects the tool.

---

## Structure of registry.json

`registry.json` is the single source of truth for which SAP R&R documents the tool knows about. Every model entry has these fields:

| Field | Type | Description |
|---|---|---|
| `short_name` | string | Brief identifier used in status.json and Claude's answers (e.g., `"PCE"`) |
| `full_name` | string | Complete official document name as published by SAP |
| `url` | string | Direct URL to download the PDF from SAP's website |
| `local_file` | string | Relative path from repo root to where the PDF is stored (e.g., `"pdfs/pce.pdf"`) |
| `last_checked` | string or null | ISO 8601 timestamp of last successful download. Set by setup.py / refresh.py. Do not edit manually. |
| `document_version` | string or null | Version string extracted from the PDF (e.g., `"v3-2026"`). Set by scripts. Do not edit manually. |
| `active` | boolean | `true` = included in downloads and Claude answers. `false` = skipped. |
| `model_family` | string | Groups models for Claude Project setup. One of: `rise_private_cloud`, `hana_enterprise_cloud`, `sovereign_cloud`, `extended_hypercare` |
| `is_supplement` | boolean | `true` if this document supplements another R&R (e.g., S4CPO, HYPERCARE) |
| `supplement_note` | string or null | Explanation shown before answers when `is_supplement` is true |

---

## How to Add a New Model

1. Open `registry.json`
2. Add a new entry at the end of the `"models"` array
3. Fill in all fields — set `last_checked` and `document_version` to `null`
4. Choose the correct `model_family` based on which Claude Project grouping it belongs to
5. Set `active: true`
6. Save the file
7. Run `python3 setup.py` — it will download the new PDF and populate the version fields
8. If the model is a supplement, update `SKILL.md` and `PROJECT_INSTRUCTIONS.md` to add the model to the auto-select rules (if needed)

**Example new entry:**
```json
{
  "short_name": "NEW_MODEL",
  "full_name": "SAP [Full Official Document Name]",
  "url": "https://www.sap.com/docs/download/...",
  "local_file": "pdfs/new_model.pdf",
  "last_checked": null,
  "document_version": null,
  "active": true,
  "model_family": "rise_private_cloud",
  "is_supplement": false,
  "supplement_note": null
}
```

---

## How to Remove or Disable a Model

Do not delete model entries from registry.json — set `active: false` instead. This preserves the history and prevents errors in status.json.

1. Open `registry.json`
2. Find the model entry
3. Change `"active": true` to `"active": false`
4. Save the file

The model will be:
- Skipped by setup.py and refresh.py
- Marked as `"status": "skipped"` in status.json
- Excluded from Claude Code answers (the skill reads `active` from the registry)

---

## How to Update a URL

When a PDF download fails with HTTP 404, the URL has most likely changed.

1. Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Filter by "Roles and Responsibilities" and "English"
3. Find the document matching the `full_name` in registry.json
4. Right-click the PDF download link and copy the URL
5. Open `registry.json`
6. Find the model entry and update the `"url"` field
7. Save the file
8. Run `python3 setup.py` or `python3 refresh.py` to retry the download

---

## How to Update a Version Note

If you want to add or update the `supplement_note` for a model:

1. Open `registry.json`
2. Find the model entry
3. Update the `supplement_note` field
4. Save the file

The updated note will appear in Claude's next session (after a `reload` command or new session start).

---

## How model_family Affects Project Grouping

The `model_family` field determines which Claude Project a model's PDF belongs in:

| model_family | Claude Project name |
|---|---|
| `rise_private_cloud` | SAP R&R — RISE Private Cloud |
| `hana_enterprise_cloud` | SAP R&R — HANA Enterprise Cloud |
| `sovereign_cloud` | SAP R&R — Sovereign Cloud |
| `extended_hypercare` | SAP R&R — Extended & HyperCare |

When you add a new model, choose the family that groups it with the most closely related existing models.

---

## When to Update SKILL.md vs registry.json

| Scenario | Update registry.json | Update SKILL.md |
|---|---|---|
| New model added | Yes | Only if you want to add auto-select keyword rules |
| URL changed | Yes | No |
| Model disabled | Yes | No |
| New supplement note | Yes | No |
| New keyword trigger for model selection | No | Yes |
| Change to answer format or confidence rules | No | Yes |

For Claude Projects (web), `PROJECT_INSTRUCTIONS.md` mirrors SKILL.md for the same answer-format changes.

---

## How to Verify Your Changes Work

After making changes to registry.json:

1. Run `python3 setup.py` (for new models or URL fixes) or `python3 refresh.py` (for incremental updates)
2. Check the printed summary table — all active models should show ✅ OK
3. Open `status.json` and verify the updated models show `"status": "ok"`
4. Start a Claude Code session and type `models` — verify the new/updated model appears
5. Ask a question about the updated model and confirm the version header shows the correct version
