# SAP ECS R&R Advisor — CLAUDE.md Template

> **FOR USERS CLONING THIS REPOSITORY:**
> Copy this file to your project root (one level above the `sap-ecs-rr-advisor/` folder).
> For example, if you cloned to `~/projects/sap-ecs-rr-advisor/`, copy this file to `~/projects/CLAUDE.md`.
> See docs/setup-claude-code.md → Step 5 for full instructions.

---

## SAP ECS R&R Advisor

At the start of every Claude Code session in this directory, automatically load the SAP ECS Roles & Responsibilities Advisor skill:

1. Read `sap-ecs-rr-advisor/SKILL.md` — these are your operating instructions for the advisor
2. Read `sap-ecs-rr-advisor/registry.json` — build the active model list
3. Read `sap-ecs-rr-advisor/status.json` — check for any failed or pending models
4. Follow all instructions in SKILL.md exactly, including the session initialisation sequence

The PDFs are stored in `sap-ecs-rr-advisor/pdfs/`. Read them as needed to answer questions — do not load all PDFs at session start, only load a PDF when the user asks about that model.

After completing the session initialisation sequence from SKILL.md, confirm you are ready with the standard ready message.
