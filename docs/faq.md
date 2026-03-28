# Frequently Asked Questions

---

## Q: Do I need Claude Pro to use this?

No, you can use this with a free Claude account. However, Claude Pro or Max is recommended for the best experience with Claude Projects, as it enables full retrieval-augmented generation (RAG) over uploaded PDFs. The free tier works but PDFs may exceed the context window for some model families, which means Claude may not read the entire document.

For Claude Code CLI, there is no difference — Pro and free accounts both work the same way.

---

## Q: How many Claude Projects do I need to set up?

One per model family that you need. There are four families:

- **RISE Private Cloud** (PCE, TAILORED, TAILORED_CDC)
- **HANA Enterprise Cloud** (HEC, HEC_ADV, HEC_CE, S4CPO)
- **Sovereign Cloud** (SOV_PCE, SOV_PCE_TAILORED, SOV_PCE_PACKAGED)
- **Extended & HyperCare** (S4EXT, HYPERCARE)

If you only work with RISE PCE deals, you only need one Project. If you work across multiple product families, set up one Project per family.

---

## Q: Why are PDFs split across multiple Projects?

Claude Projects have limits on the total content that can be uploaded per Project. Splitting by model family keeps each Project within these limits and ensures Claude can read the full content of each PDF without truncation.

It also mirrors how SAP organises its products — each family has distinct deployment models and responsibilities, so keeping them in separate Projects reduces the risk of Claude confusing responsibilities across product lines.

---

## Q: How do I know when SAP updates a document?

Claude includes the document version number in every answer header (e.g., `Version: v3-2026`). Check this against the version shown in the filename on SAP's website quarterly:

1. Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
2. Look for each document and note the version in the filename
3. If the version on SAP's site is newer than what Claude reports, it is time to refresh

For CLI users, `refresh.py` handles this automatically every Sunday — it will detect if the version has changed and re-download only the updated PDFs.

---

## Q: The version shown seems old — what should I do?

**CLI users:** Run `python3 refresh.py` manually. If the version is still old after the refresh, SAP may not have published a newer version yet, or the URL in registry.json may need updating.

**Web users:** Download the PDF fresh from SAP's website, delete the old one from your Claude Project, and upload the new one. If the new download has the same version number as what Claude reports, the document has not been updated.

---

## Q: Can I use this for official customer commitments?

No. This tool is for research and preparation purposes only. Always refer to the official SAP documentation at [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html) and your specific contract for any contractual or commercial commitments.

The tool includes a confidence rating on every answer to help you judge when to verify directly in the source document. Always verify Low and Medium confidence answers against the PDF before using them in a customer context.

---

## Q: Why does Claude sometimes say it's not sure?

The confidence rating system is intentional. SAP's R&R documents are detailed legal documents with conditions, footnotes, and service category distinctions. When a question:

- Is not directly addressed in a section (only inferred)
- Has conditions or footnotes that change the answer
- Spans multiple conflicting sections
- Depends on a service category that wasn't specified

...Claude will rate confidence as Medium or Low and explain why. This is the correct behaviour. A false "High" confidence rating on an ambiguous answer would be more dangerous than an honest "Medium."

---

## Q: What does "Supplement" mean for S4CPO and HyperCare?

Supplement documents do not stand alone — they modify or extend the responsibilities defined in a base R&R document.

- **S4CPO** supplements the **HEC** R&R. When using S4CPO, you need both HEC and S4CPO to get the complete picture of responsibilities.
- **HYPERCARE** supplements your **primary R&R model** (PCE, Tailored, HEC, etc.). It describes responsibilities specifically for the HyperCare service period and must be read alongside your base contract's R&R.

Claude will always show the supplement note before answering questions about these documents, reminding you to read them alongside the base document.

---

## Q: How is this different from SAP's official documentation?

SAP's official R&R documents are the PDFs themselves — dense, multi-page legal documents that require careful reading to extract a specific answer. This tool does not replace them; it provides a conversational interface over them.

This is a community project. It is not endorsed by, affiliated with, or supported by SAP SE or any SAP entity. SAP's official documentation at [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html) is always the authoritative source.

---

## Q: Can I contribute to this project?

Yes. Contributions are welcome:

- **Found a broken URL?** Open an issue with the correct URL.
- **SAP added a new document?** Open a PR adding it to registry.json.
- **Writing Windows setup docs?** Open a PR for docs/setup-windows.md.
- **Found a bug or improvement?** Open an issue or PR.

Repository: [https://github.com/jayeshvorani/sap-ecs-rr-advisor](https://github.com/jayeshvorani/sap-ecs-rr-advisor)

---

## Q: I found a bug — how do I report it?

Open an issue at [https://github.com/jayeshvorani/sap-ecs-rr-advisor/issues](https://github.com/jayeshvorani/sap-ecs-rr-advisor/issues) with:

- What you were trying to do
- What you expected to happen
- What actually happened
- Any error messages shown (copy the full output)
- Your operating system and Python version (`python3 --version`)
