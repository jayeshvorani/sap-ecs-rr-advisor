# Setting Up SAP ECS R&R Advisor — Claude Code CLI

This guide sets up the advisor for Claude Code CLI users. PDFs are stored locally on your machine and refresh automatically every Sunday.

---

## Prerequisites

Before starting, ensure you have:

- **Claude Code CLI** installed — see [https://docs.anthropic.com/claude-code](https://docs.anthropic.com/claude-code)
- **Python 3.10 or higher** — see Step 2 below
- **pdftotext** — installed via Homebrew (Mac) — see Step 2 below
- A Mac (Windows support is coming — see [docs/setup-windows.md](setup-windows.md))

---

## Step 1: Clone the Repository

```bash
cd ~/Documents/Claude_Code_Projects    # or your preferred parent directory
git clone https://github.com/jayeshvorani/sap-ecs-rr-advisor.git
cd sap-ecs-rr-advisor
```

---

## Step 2: Set Up Your Python Environment

Follow the Mac-specific setup guide: [docs/setup-mac.md](setup-mac.md)

This covers:
- Installing Homebrew (if not already installed)
- Installing Python via Homebrew
- Creating a virtual environment at the correct path
- Installing the `requests` library
- Verifying `pdftotext` is available

---

## Step 3: Update the Shebang in setup.py and refresh.py

Both scripts have a hardcoded shebang that points to the repo author's Python virtual environment. You must update these to point to your own venv.

Open each file and update line 1:

**setup.py — line 1:**
```
# Current (repo author's path — do not use as-is):
#!/Users/I553472/Documents/Claude_Code_Projects/.venv/bin/python3

# Change to your venv path, for example:
#!/Users/yourname/Documents/Claude_Code_Projects/.venv/bin/python3
# or:
#!/usr/bin/env python3
```

**refresh.py — line 1:**
Same change as above.

If you are using `#!/usr/bin/env python3`, ensure your venv is active when running the scripts, or use `python3 setup.py` / `python3 refresh.py` directly.

---

## Step 4: Run setup.py

From the `sap-ecs-rr-advisor/` directory:

```bash
python3 setup.py
```

This will:
1. Check your environment (pdftotext, requests, pdfs/ directory)
2. Download all 12 PDFs from SAP's website
3. Extract version strings from each PDF
4. Update `registry.json` with version and last-checked date
5. Update `status.json` with download results
6. Print a summary table

The download takes 1–3 minutes depending on your connection speed.

**If any downloads fail:**
- Note which models failed and the error shown
- Visit [https://www.sap.com/about/agreements/policies/hec-services.html](https://www.sap.com/about/agreements/policies/hec-services.html)
- Find the current URL for the failed document
- Update the `"url"` field in `registry.json`
- Run `python3 setup.py` again — it will retry all models

---

## Step 5: Set Up CLAUDE.md for Automatic Skill Loading

The repository includes a `CLAUDE.md` template that tells Claude Code to load the R&R Advisor skill at the start of every session.

Copy it to your project root (one level above the `sap-ecs-rr-advisor/` folder):

```bash
# If your parent directory is ~/Documents/Claude_Code_Projects:
cp sap-ecs-rr-advisor/CLAUDE.md ../CLAUDE.md
```

Or copy it to your home directory if you want the skill available everywhere:

```bash
cp sap-ecs-rr-advisor/CLAUDE.md ~/CLAUDE.md
```

> **Note:** Claude Code loads CLAUDE.md files from the current working directory and all parent directories up to your home directory. Place it wherever makes sense for how you work.

**What CLAUDE.md does:**
At the start of every Claude Code session in that directory, Claude will automatically:
1. Read `SKILL.md` for operating instructions
2. Read `registry.json` for the model list
3. Read `status.json` for PDF download status
4. Confirm it is ready with a status message

---

## Step 6: Set Up the Launchd Schedule (Automatic Weekly Refresh)

This step schedules `refresh.py` to run automatically every Sunday at 08:00. This keeps your PDFs current without any manual action.

### 6a. Prepare the plist file

The repository includes a template plist at `com.jayeshvorani.rr-refresh.plist`. Edit it to replace the placeholder paths with your own:

1. Open `com.jayeshvorani.rr-refresh.plist` in a text editor
2. Replace `/REPLACE/WITH/YOUR/VENV/PATH/python3` with your actual venv path
   - Example: `/Users/yourname/Documents/Claude_Code_Projects/.venv/bin/python3`
3. Replace `/REPLACE/WITH/YOUR/REPO/PATH/sap-ecs-rr-advisor/refresh.py` with your actual path
   - Example: `/Users/yourname/Documents/Claude_Code_Projects/sap-ecs-rr-advisor/refresh.py`
4. Replace `REPLACE_USERNAME` in the log paths with your macOS username

### 6b. Copy to LaunchAgents

```bash
cp com.jayeshvorani.rr-refresh.plist ~/Library/LaunchAgents/
```

### 6c. Load the schedule

```bash
launchctl load ~/Library/LaunchAgents/com.jayeshvorani.rr-refresh.plist
```

### 6d. Test it (optional but recommended)

```bash
launchctl start com.jayeshvorani.rr-refresh
```

Then check the log:
```bash
tail -f ~/Library/Logs/rr-refresh-stdout.log
```

### Other launchd commands

```bash
# Check status
launchctl list | grep rr-refresh

# Unload (stops automatic scheduling)
launchctl unload ~/Library/LaunchAgents/com.jayeshvorani.rr-refresh.plist
```

---

## Step 7: Test with a Sample Question

Start Claude Code in your project directory:

```bash
claude
```

Claude will load the skill automatically from CLAUDE.md and show a ready confirmation. Then ask a test question:

```
Who is responsible for OS patching under the PCE model?
```

A good response will:
- Show a version header with the document version
- Give a direct answer
- Include a responsibility table with section reference
- Show a confidence rating

---

## Step 8: Running a Manual Refresh

At any time, refresh all PDFs:

```bash
python3 refresh.py
```

Refresh only re-downloads PDFs where the version has changed or the file is missing. It skips models that are already current, so it is safe to run at any time.

After a refresh, if any model versions have changed, you will see:
```
📄 Updated models require re-upload to Claude Projects.
   See docs/setup-web-projects.md → Keeping PDFs current.
```
