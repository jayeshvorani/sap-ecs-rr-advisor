# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-03-28

### Added
- Initial release
- 12 SAP ECS R&R models across 4 model families (RISE Private Cloud, HANA Enterprise Cloud, Sovereign Cloud, Extended & HyperCare)
- `registry.json` — single source of truth for all model metadata, URLs, and version tracking
- `status.json` — automated download status tracking per model
- `setup.py` — one-time setup script: downloads all active PDFs, extracts version strings, updates registry and status atomically
- `refresh.py` — incremental refresh script: skips current models, detects version changes, trims logs older than 30 days
- `SKILL.md` — Claude Code CLI skill with full session initialisation, model auto-selection, version headers, responsibility tables, confidence ratings, and persona switching
- `PROJECT_INSTRUCTIONS.md` — Claude Projects instructions for web users, identical logic adapted for Projects context
- `CLAUDE.md` — template for auto-loading the skill at Claude Code session start
- LaunchD plist for automatic weekly PDF refresh every Sunday at 08:00 (Mac)
- Repo copy of plist (`com.sap.rr.refresh.plist`) with placeholder paths for other users
- `docs/setup-web-projects.md` — step-by-step guide for Claude Projects setup
- `docs/setup-claude-code.md` — step-by-step guide for Claude Code CLI setup
- `docs/setup-mac.md` — Mac Python environment setup guide
- `docs/setup-windows.md` — Windows placeholder with interim web path
- `docs/managing-models.md` — comprehensive registry.json field reference and maintenance guide
- `docs/troubleshooting.md` — error-by-error troubleshooting for download failures, Claude Code, and Claude Projects
- `docs/faq.md` — 11 frequently asked questions
- Comprehensive error handling: per-model failures do not stop other downloads; all failures reported with actionable instructions
- Atomic file writes throughout — registry.json and status.json never corrupted on failure
- Structured logging to `logs/setup.log` and `logs/refresh.log`
