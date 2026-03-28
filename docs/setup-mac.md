# Mac Environment Setup

This guide sets up the Python environment needed to run `setup.py` and `refresh.py` on macOS.

The scripts require:
- Python 3.10 or higher
- The `requests` library
- `pdftotext` (from the Poppler PDF toolkit)

---

## Step 1: Install Homebrew

If you do not already have Homebrew installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, follow any instructions Homebrew prints — you may need to add it to your PATH. For Apple Silicon Macs (M1/M2/M3), Homebrew installs to `/opt/homebrew/`. For Intel Macs, it installs to `/usr/local/`.

Verify Homebrew works:
```bash
brew --version
```

---

## Step 2: Install Python via Homebrew

```bash
brew install python
```

After installation, verify:
```bash
/opt/homebrew/bin/python3 --version
# Should show Python 3.x.x
```

> **Note:** macOS includes a system Python at `/usr/bin/python3`, but it is intentionally limited. Always use the Homebrew Python for this project.

**Fix PATH if needed:**

If `python3` in your terminal does not point to the Homebrew version, add Homebrew to your PATH:

```bash
# For zsh (default on modern macOS):
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For bash:
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

---

## Step 3: Install pdftotext (Poppler)

```bash
brew install poppler
```

Verify installation:
```bash
/opt/homebrew/bin/pdftotext -v
# Should show: pdftotext version x.x.x
```

The scripts expect `pdftotext` at `/opt/homebrew/bin/pdftotext`. If you are on an Intel Mac where Homebrew uses `/usr/local/`, update this path in `setup.py` and `refresh.py`:

```python
# Line in both scripts — update if needed:
PDFTOTEXT = "/opt/homebrew/bin/pdftotext"
# Intel Mac alternative:
# PDFTOTEXT = "/usr/local/bin/pdftotext"
```

---

## Step 4: Create a Virtual Environment

Create the virtual environment at the standard path used by this project:

```bash
# Navigate to the parent directory of your repo
cd ~/Documents/Claude_Code_Projects
# (Replace with your own path)

# Create the venv
/opt/homebrew/bin/python3 -m venv .venv
```

Verify it was created:
```bash
ls .venv/bin/python3
# Should output the path
```

---

## Step 5: Install the requests Library

```bash
.venv/bin/pip install requests
```

Verify:
```bash
.venv/bin/python3 -c "import requests; print(requests.__version__)"
# Should print the version number, e.g. 2.31.0
```

---

## Step 6: Update the Shebang (if you are not the repo author)

If your virtual environment is at a different path than `~/Documents/Claude_Code_Projects/.venv/`, update the first line of both scripts:

**setup.py and refresh.py — line 1:**
```bash
# Both scripts use the portable shebang by default:
#!/usr/bin/env python3

# This works as long as python3 resolves to your venv python, or you activate the venv first.
# If you need to hardcode the path, change to your actual venv path, e.g.:
#!/Users/yourname/Documents/Claude_Code_Projects/.venv/bin/python3
```

---

## Verification Checklist

Run this to confirm your environment is ready:

```bash
# 1. Python version
/opt/homebrew/bin/python3 --version
# Expected: Python 3.10.x or higher

# 2. pdftotext
/opt/homebrew/bin/pdftotext -v
# Expected: version output

# 3. requests
.venv/bin/python3 -c "import requests; print('requests OK')"
# Expected: requests OK

# 4. venv python
ls .venv/bin/python3
# Expected: file exists
```

Once all checks pass, return to [docs/setup-claude-code.md](setup-claude-code.md) and continue from Step 4.
