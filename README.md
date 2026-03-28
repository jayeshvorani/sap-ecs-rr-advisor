# SAP ECS Roles & Responsibilities Advisor

![Version](https://img.shields.io/badge/version-v1.0-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![PDFs](https://img.shields.io/badge/PDFs-12%20models-orange)

---

## What This Tool Does

The SAP ECS Roles & Responsibilities Advisor lets you ask plain-language questions about the contractual responsibilities in SAP Enterprise Cloud Services engagements — and get precise, document-backed answers with section references, responsibility tables, and confidence ratings.

Instead of hunting through dense PDF documents to find out whether SAP or the customer owns a particular task, you ask Claude directly: *"Who is responsible for homogeneous system copies in the PCE model?"* and get a structured answer with the exact section cited, any conditions or footnotes noted, and a confidence rating. It works across all 12 official SAP ECS R&R documents, supports cross-model comparisons, and keeps track of document versions so you always know how fresh your answers are.

---

## What You Can Ask

```
"Who is responsible for OS patching in the PCE model?"

"What are SAP's limits on system refreshes per year under HEC?"

"Compare PCE and Tailored — who owns database backups in each?"

"Is HyperCare included in my standard contract or is it additional?"

"What does SAP cover for the Customer Data Center option that the
 standard Tailored model doesn't?"

"Under Sovereign Cloud PCE, who manages network configuration?"

"Give me a simple answer on HEC responsibilities for basis operations
 — sales view."

"What's the difference in system copy limits between HEC and HEC
 Advanced Edition?"
```

---

## What You Need

- A **Claude account** — free or paid at [claude.ai](https://claude.ai)
- **Claude Pro or Max** is recommended for Claude Projects (enables RAG over uploaded PDFs). The free tier can use Projects but is limited to the context window, which may not fit all PDFs for a model family.
- **Technical users** using Claude Code CLI need Python 3.10+ and `pdftotext` (installed via Homebrew on Mac).

---

## Choose Your Setup Path

```
→ I want the easiest setup (recommended for most users)
  No installation. Works in your browser.
  ▶ Use Claude Projects → docs/setup-web-projects.md

→ I use Claude Code CLI
  PDFs stored locally. Automatic weekly refresh.
  ▶ Claude Code setup → docs/setup-claude-code.md
```

---

## Model Families

SAP publishes 12 R&R documents across four product families. Because Claude Projects have file limits, PDFs are organised into one Project per family.

### RISE Private Cloud Project
| Short Name | Full Name | Notes |
|---|---|---|
| PCE | SAP S/4HANA Cloud, private edition and SAP ERP, PCE Roles and Responsibilities | |
| TAILORED | SAP S/4HANA Cloud, private edition and SAP ERP, Tailored Option Roles and Responsibilities | |
| TAILORED_CDC | SAP S/4HANA Cloud, private edition and SAP ERP, Tailored Option - Customer Data Center Option | |

### HANA Enterprise Cloud Project
| Short Name | Full Name | Notes |
|---|---|---|
| HEC | SAP HANA Enterprise Cloud Roles and Responsibilities for Production (BYOL and Subscription models) | |
| HEC_ADV | SAP HANA Enterprise Cloud, Advanced Edition Roles and Responsibilities (BYOL and Subscription Models) | |
| HEC_CE | SAP HANA Enterprise Cloud Customer Edition | |
| S4CPO | SAP HANA Enterprise Cloud Roles and Responsibilities Supplement for S4CPO | Supplement — use alongside HEC. Document is v3-2023; verify currency with SAP. |

### Sovereign Cloud Project
| Short Name | Full Name | Notes |
|---|---|---|
| SOV_PCE | SAP Sovereign Cloud PCE Roles and Responsibilities | |
| SOV_PCE_TAILORED | SAP Sovereign Cloud PCE Tailored Roles and Responsibilities | |
| SOV_PCE_PACKAGED | SAP Sovereign Cloud PCE Packaged Roles and Responsibilities | |

### Extended & HyperCare Project
| Short Name | Full Name | Notes |
|---|---|---|
| S4EXT | SAP S/4HANA Cloud, Extended Edition Roles and Responsibilities for Production | |
| HYPERCARE | SAP ECS HyperCare Service Description Supplement to Roles and Responsibilities | Supplement — use alongside your primary R&R model. |

---

## Managing Model Changes

SAP periodically publishes new R&R documents or updates existing ones. Here is how to keep the tool current.

### If SAP adds a new R&R document

1. Open `registry.json`
2. Add a new entry at the end of the `"models"` array (see format below)
3. Set `"active": true`, `"last_checked": null`, `"document_version": null`
4. Run `python3 setup.py` — it will download the new PDF and populate the version

### If SAP removes an R&R document

1. Open `registry.json`
2. Find the model entry and set `"active": false`
3. The model will be skipped by setup.py and refresh.py, and excluded from Claude answers

### If a PDF URL changes (download fails)

1. Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Filter by "Roles and Responsibilities" and "English"
3. Find the document and copy the PDF download URL
4. Open `registry.json` and update the `"url"` field for the affected model
5. Run `python3 setup.py` — failed models are retried on every run

### Format of registry.json entries

```json
{
  "short_name": "PCE",
  "full_name": "SAP S/4HANA Cloud, private edition and SAP ERP, PCE Roles and Responsibilities",
  "url": "https://www.sap.com/docs/download/...",
  "local_file": "pdfs/pce.pdf",
  "last_checked": null,
  "document_version": null,
  "active": true,
  "model_family": "rise_private_cloud",
  "is_supplement": false,
  "supplement_note": null
}
```

For full field-by-field documentation, see [docs/managing-models.md](docs/managing-models.md).

---

## Keeping PDFs Current

SAP updates R&R documents periodically. Here is how to stay current on each setup path.

**CLI users (Claude Code):**
`refresh.py` runs automatically every Sunday at 08:00 via launchd. To refresh manually at any time:
```
python3 refresh.py
```
Claude will report the document version in every answer — if the version looks old, run a manual refresh.

**Web users (Claude Projects):**
Check quarterly. When SAP publishes a new version:
1. Visit [SAP's R&R page](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Download the updated PDF for your model
3. Open your Claude Project
4. Delete the old PDF file from the Project knowledge base
5. Upload the new PDF

**How do you know when SAP updates a PDF?**
The version string changes — for example, `v3-2025` becomes `v3-2026`. Claude includes the document version in every answer header. If the version you see does not match the latest on SAP's website, it is time to refresh.

---

## Disclaimer

This is a personal community project and does not represent an official SAP product, service, or communication. Responsibility assignments shown are derived from publicly available SAP documentation and are provided for informational purposes only. Always refer to the official SAP documentation at [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html) for contractual and commercial purposes.

---

## Contributing

Found a broken URL? SAP added a new document? Open an issue or submit a pull request — contributions welcome.

[https://github.com/jayeshvorani/sap-ecs-rr-advisor](https://github.com/jayeshvorani/sap-ecs-rr-advisor)

---

## License

MIT License — see [LICENSE](LICENSE) for full text.
