# Setting Up SAP ECS R&R Advisor — Claude Projects (Web)

No coding required. This guide walks you through setting up the advisor in Claude's browser interface using Claude Projects.

---

## What You Need

- A Claude account (free or paid) at [claude.ai](https://claude.ai)
- Claude Pro or Max is recommended — it enables full RAG (retrieval-augmented generation) over your uploaded PDFs. The free tier works but PDFs may exceed the context window for some model families.
- A browser. No software to install.

---

## Step 1: Get the Project Instructions

1. Go to [https://github.com/jayeshvorani/sap-ecs-rr-advisor](https://github.com/jayeshvorani/sap-ecs-rr-advisor)
2. Click on the file `PROJECT_INSTRUCTIONS.md`
3. Click the **Raw** button to view the plain text version
4. Select all text (Ctrl+A / Cmd+A) and copy it (Ctrl+C / Cmd+C)

---

## Step 2: Create Your First Claude Project

1. Go to [claude.ai](https://claude.ai) and sign in
2. In the left sidebar, click **Projects**
3. Click **New Project**
4. Name the Project — we recommend one of these names:
   - `SAP R&R — RISE Private Cloud`
   - `SAP R&R — HANA Enterprise Cloud`
   - `SAP R&R — Sovereign Cloud`
   - `SAP R&R — Extended & HyperCare`
5. Find the **Custom Instructions** field (sometimes labelled "Project Instructions")
6. Paste the content you copied from PROJECT_INSTRUCTIONS.md
7. Click **Save**

---

## Step 3: Download the PDFs for Your Model Family

Download the PDFs for the model family that matches your Project. Click each URL to download the PDF directly to your computer.

### RISE Private Cloud Project

| Model | Full Name | PDF URL |
|---|---|---|
| PCE | SAP S/4HANA Cloud, private edition and SAP ERP, PCE Roles and Responsibilities | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-s4hana-cloud-private-edition-and-sap-erp-pce-roles-and-responsibilities-english-v3-2026.pdf) |
| TAILORED | SAP S/4HANA Cloud, private edition and SAP ERP, Tailored Option R&R | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-s4hana-cloud-private-edition-and-sap-erp-tailored-option-roles-and-responsibilities-english-v3-2026.pdf) |
| TAILORED_CDC | SAP S/4HANA Cloud, private edition and SAP ERP, Tailored Option - Customer Data Center Option | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-s4hana-cloud-private-edition-and-sap-erp-tailored-option-customer-data-center-option-english-v3-2026.pdf) |

### HANA Enterprise Cloud Project

| Model | Full Name | PDF URL |
|---|---|---|
| HEC | SAP HANA Enterprise Cloud R&R for Production (BYOL and Subscription models) | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-hana-enterprise-cloud-roles-and-responsibilities-for-production-byol-and-subscription-models-english-v3-2026.pdf) |
| HEC_ADV | SAP HANA Enterprise Cloud, Advanced Edition R&R (BYOL and Subscription Models) | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-hana-enterprise-cloud-advanced-edition-roles-and-responsibilities-byol-and-subscription-models-english-v3-2026.pdf) |
| HEC_CE | SAP HANA Enterprise Cloud Customer Edition | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-hana-enterprise-cloud-customer-edition-english-v3-2026.pdf) |
| S4CPO | SAP HANA Enterprise Cloud R&R Supplement for S4CPO | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-hana-enterprise-cloud-roles-and-responsibilities-supplement-for-s4cpo-english-v3-2023.pdf) |

### Sovereign Cloud Project

| Model | Full Name | PDF URL |
|---|---|---|
| SOV_PCE | SAP Sovereign Cloud PCE Roles and Responsibilities | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-sovereign-cloud-pce-roles-and-responsibilities-english-v7-2025.pdf) |
| SOV_PCE_TAILORED | SAP Sovereign Cloud PCE Tailored Roles and Responsibilities | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-sovereign-cloud-pce-tailored-roles-and-responsibilities-english-v3-2026a.pdf) |
| SOV_PCE_PACKAGED | SAP Sovereign Cloud PCE Packaged Roles and Responsibilities | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-sovereign-cloud-pce-packaged-roles-and-responsibilities-english-v3-2026b.pdf) |

### Extended & HyperCare Project

| Model | Full Name | PDF URL |
|---|---|---|
| S4EXT | SAP S/4HANA Cloud, Extended Edition R&R for Production | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-s4hana-cloud-extended-edition-roles-and-responsibilities-for-production-english-v3-2026.pdf) |
| HYPERCARE | SAP ECS HyperCare Service Description Supplement to R&R | [Download](https://www.sap.com/docs/download/agreements/product-policy/hec/roles-responsibilities/sap-ecs-hypercare-service-description-supplement-to-roles-and-responsibilities-english-v3-2026.pdf) |

> **Important:** Download the PDFs directly from your browser. Do not rename the files — the filenames are not critical, but keeping them as downloaded avoids confusion.

---

## Step 4: Upload PDFs to Your Project

1. Open your Claude Project
2. Click **Add Content** (or the upload/attachment icon)
3. Click **Upload files**
4. Select all PDFs for this Project's model family
5. Wait for each upload to show a confirmation indicator before proceeding
6. Verify all PDFs are listed in your Project's knowledge base

---

## Step 5: Test It

1. Open a new chat within your Project (click **New chat** or **New conversation** inside the Project)
2. Ask a test question, for example:
   - For RISE Private Cloud: *"Who is responsible for OS patching under PCE?"*
   - For HANA Enterprise Cloud: *"What are SAP's limits on system refreshes per year under HEC?"*
3. A good response will:
   - Show a version header with the document version number
   - Give a direct answer followed by a responsibility table
   - Cite a specific section identifier (e.g., `Per BASIC_1.3.10B`)
   - Include a confidence rating

If Claude gives a vague answer without section references, check that your Project Instructions were saved correctly (Step 2).

---

## Keeping PDFs Current (Quarterly Refresh)

SAP updates R&R documents periodically. Check quarterly:

1. Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Filter by "Roles and Responsibilities" and "English"
3. Compare the version in the filename (e.g., `v3-2026`) to what Claude reports in its version header
4. If SAP has published a newer version:
   - Download the updated PDF
   - Open your Claude Project
   - Delete the old PDF from the Project knowledge base
   - Upload the new PDF

---

## Creating Additional Projects for Other Model Families

Repeat Steps 2–5 for each model family you need:
- One Project per family (RISE Private Cloud, HANA Enterprise Cloud, Sovereign Cloud, Extended & HyperCare)
- Each Project uses the same `PROJECT_INSTRUCTIONS.md`
- Each Project contains only the PDFs for its model family

---

## Troubleshooting

**PDF upload fails:**
- Check file size — Claude Projects have per-file and total size limits
- Ensure the file is a valid PDF (open it in your browser to confirm it downloaded correctly)
- Try uploading one file at a time

**Claude ignores the instructions:**
- Confirm the Project Instructions were saved (open Project settings and check the instructions field is populated)
- Start a fresh chat within the Project — do not use a chat that was started before the instructions were saved

**PDF appears outdated:**
- Check the version header in Claude's response
- Visit SAP's R&R page and compare the version number
- If SAP has a newer version, follow the quarterly refresh steps above

**Link in the table returns a 404:**
- SAP has moved or updated the document
- Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html) to find the current URL
- Open an issue at [https://github.com/jayeshvorani/sap-ecs-rr-advisor](https://github.com/jayeshvorani/sap-ecs-rr-advisor) with the updated URL
