# Installation Guide - HW Helper

## Quick Start (3 Steps)

### Option 1: Clone from GitHub (Recommended - Always Latest)

```bash
# 1. Clone the repository
git clone https://github.com/c26609124-sketch/hw-helper.git

# 2. Navigate to directory
cd hw-helper

# 3. Install dependencies and run
pip install -r requirements.txt
python ui.py
```

**That's it!** The app will auto-update whenever you run it.

---

### Option 2: Download ZIP (Simple)

1. **Download**: Go to https://github.com/c26609124-sketch/hw-helper
2. Click green **"Code"** button → **"Download ZIP"**
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder
5. Run:
   ```bash
   pip install -r requirements.txt
   python ui.py
   ```

---

## Detailed Installation Instructions

### Windows

#### Step 1: Install Python (if not installed)
1. Download Python 3.10+ from https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

#### Step 2: Download the App

**Method A: Using Git**
```cmd
# Install git if needed: https://git-scm.com/download/win
git clone https://github.com/c26609124-sketch/hw-helper.git
cd hw-helper
```

**Method B: Download ZIP**
1. Visit https://github.com/c26609124-sketch/hw-helper
2. Click **Code** → **Download ZIP**
3. Extract to `C:\Users\YourName\hw-helper`

#### Step 3: Install Dependencies
```cmd
cd C:\Users\YourName\hw-helper
pip install -r requirements.txt
```

#### Step 4: Run the App
```cmd
python ui.py
```

---

### macOS

#### Step 1: Install Python (if not installed)
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

#### Step 2: Download the App

**Method A: Using Git**
```bash
git clone https://github.com/c26609124-sketch/hw-helper.git
cd hw-helper
```

**Method B: Download ZIP**
1. Visit https://github.com/c26609124-sketch/hw-helper
2. Click **Code** → **Download ZIP**
3. Extract to `~/hw-helper`

#### Step 3: Install Dependencies
```bash
cd ~/hw-helper
pip3 install -r requirements.txt
```

#### Step 4: Run the App
```bash
python3 ui.py
```

---

### Linux

#### Step 1: Install Python (usually pre-installed)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip git

# Fedora
sudo dnf install python3 python3-pip git

# Arch
sudo pacman -S python python-pip git
```

#### Step 2: Download the App
```bash
git clone https://github.com/c26609124-sketch/hw-helper.git
cd hw-helper
```

#### Step 3: Install Dependencies
```bash
pip3 install -r requirements.txt
```

#### Step 4: Run the App
```bash
python3 ui.py
```

---

## Configuration

### First Launch Setup

1. **API Key**: Enter your OpenRouter API key in Settings
   - Get one from: https://openrouter.ai/keys
   - Click "Save Settings"

2. **AI Model**: Select your preferred model
   - Recommended: `google/gemini-2.5-flash`
   - Free options available

3. **Test**: Load a screenshot and click "Get AI Answer"

---

## Auto-Update System

The app automatically checks for updates on startup:

```
App starts
   ↓
Checks GitHub for latest version
   ↓
If update available:
   • Shows changelog
   • Downloads update
   • Applies changes
   • Prompts restart
   ↓
You're always on the latest version!
```

**Current Version**: 1.0.1
**Repository**: https://github.com/c26609124-sketch/hw-helper

---

## Required Dependencies

The app will install these automatically from `requirements.txt`:

```
customtkinter>=5.2.0
Pillow>=10.0.0
requests>=2.31.0
```

**Optional** (for browser capture):
- Selenium (if using browser automation)
- ChromeDriver (for Chrome browser control)

---

## Troubleshooting

### "python not found"
**Windows**: Make sure "Add Python to PATH" was checked during installation
**Mac/Linux**: Use `python3` instead of `python`

### "pip not found"
```bash
# Windows
python -m pip install -r requirements.txt

# Mac/Linux
python3 -m pip install -r requirements.txt
```

### "ModuleNotFoundError: No module named 'customtkinter'"
```bash
pip install customtkinter
```

### Updates not downloading
1. Check internet connection
2. Verify GitHub is accessible: https://github.com/c26609124-sketch/hw-helper
3. Check Activity Log in the app for error messages

### Permission errors
**Windows**: Run as Administrator
**Mac/Linux**: Use `sudo pip3 install ...` if needed

---

## Different Machine Setup

### Moving from Machine A to Machine B

**Best Practice**: Use Git clone (always gets latest version)

**Option 1: Fresh Install (Recommended)**
```bash
# On Machine B
git clone https://github.com/c26609124-sketch/hw-helper.git
cd hw-helper
pip install -r requirements.txt
python ui.py
```

**Option 2: Copy Files**
1. Zip the folder on Machine A
2. Transfer to Machine B
3. Extract and run:
   ```bash
   cd hw-helper
   pip install -r requirements.txt
   python ui.py
   ```

**Note**: Auto-updater will sync you to the latest version regardless!

---

## Updating Manually

If auto-update fails or you want to update manually:

### If installed via Git:
```bash
cd hw-helper
git pull origin main
pip install -r requirements.txt --upgrade
python ui.py
```

### If downloaded as ZIP:
1. Download new ZIP from GitHub
2. Extract to same location (overwrite files)
3. Run `pip install -r requirements.txt --upgrade`

---

## Files That Persist

These files are **NOT** overwritten during updates (your data is safe):

- `api_key.txt` - Your API key
- `screenshots/` - Your saved screenshots
- `saved_screenshots/` - Your saved screenshots
- `config.json` - Your settings

---

## System Requirements

**Minimum**:
- Python 3.10 or higher
- 2 GB RAM
- Internet connection (for AI API calls)
- 100 MB free disk space

**Recommended**:
- Python 3.11+
- 4 GB RAM
- Fast internet connection
- 500 MB free disk space

**Supported OS**:
- ✅ Windows 10/11
- ✅ macOS 11+ (Big Sur or later)
- ✅ Linux (Ubuntu 20.04+, Fedora 35+, Arch)

---

## Quick Reference

### Windows
```cmd
# Clone
git clone https://github.com/c26609124-sketch/hw-helper.git
cd hw-helper

# Install
pip install -r requirements.txt

# Run
python ui.py
```

### macOS / Linux
```bash
# Clone
git clone https://github.com/c26609124-sketch/hw-helper.git
cd hw-helper

# Install
pip3 install -r requirements.txt

# Run
python3 ui.py
```

---

## Getting Help

- **GitHub Issues**: https://github.com/c26609124-sketch/hw-helper/issues
- **Documentation**: See README.md in the repository
- **Check Logs**: Activity Log in the app shows detailed information

---

## Version Information

**Current Release**: v1.0.1
**Release Date**: 2025-10-29

**Latest Changes**:
- Fixed text cutoff in dropdown questions
- Improved text wrapping
- Auto-update system enabled

**Full Changelog**: See `version.json` or GitHub releases

---

**Ready to Go!**

1. Clone or download from GitHub
2. Install dependencies
3. Run `python ui.py`
4. Enter API key
5. Start using!

The app will keep itself updated automatically. 🎉
