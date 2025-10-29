#!/bin/bash
# ============================================================
# Homework Helper AI - Automated Setup and Launch Script
# Unix/Linux/macOS Shell Script for Non-Technical Users
# ============================================================

echo ""
echo "========================================"
echo " Homework Helper AI Setup"
echo "========================================"
echo ""

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Detect Python
echo "[1/5] Detecting Python installation..."

PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "   Found: python3 ($PYTHON_VERSION)"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    # Check if it's Python 3
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        echo "   Found: python ($PYTHON_VERSION)"
        PYTHON_CMD="python"
    else
        echo -e "${YELLOW}   Warning: Found Python 2, need Python 3${NC}"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo -e "${RED}[ERROR] Python 3 not found!${NC}"
    echo ""
    echo "Please install Python 3 from:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3"
    echo "  - macOS: brew install python3  (or download from python.org)"
    echo "  - Fedora: sudo dnf install python3"
    echo ""
    exit 1
fi

echo "   Python detected: $PYTHON_CMD"

# Step 2: Detect pip
echo ""
echo "[2/5] Detecting pip installation..."

PIP_CMD=""

if command -v pip3 &> /dev/null; then
    echo "   Found: pip3"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    echo "   Found: pip"
    PIP_CMD="pip"
elif $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "   Found: $PYTHON_CMD -m pip"
    PIP_CMD="$PYTHON_CMD -m pip"
fi

if [ -z "$PIP_CMD" ]; then
    echo ""
    echo -e "${RED}[ERROR] pip not found!${NC}"
    echo ""
    echo "Please install pip using:"
    echo "   $PYTHON_CMD -m ensurepip --upgrade"
    echo ""
    echo "Or install via package manager:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3-pip"
    echo "  - macOS: pip should come with Python from Homebrew"
    echo "  - Fedora: sudo dnf install python3-pip"
    echo ""
    exit 1
fi

echo "   pip detected: $PIP_CMD"

# Step 3: Install requirements
echo ""
echo "[3/5] Installing Python dependencies..."
echo "   This may take a few minutes..."
echo ""

if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}[ERROR] Failed to install requirements!${NC}"
        echo ""
        echo "Please check your internet connection and try again."
        echo "If the problem persists, install manually:"
        echo "   $PIP_CMD install customtkinter Pillow selenium requests protobuf"
        echo ""
        exit 1
    fi
else
    echo -e "${YELLOW}   Warning: requirements.txt not found${NC}"
    echo "   Installing core dependencies manually..."
    $PIP_CMD install customtkinter Pillow selenium requests protobuf
fi

echo ""
echo "   All dependencies installed successfully!"

# Step 4: Check for Brave browser
echo ""
echo "[4/5] Checking for Brave browser..."

BRAVE_PATH=""

# Check common Brave installation paths
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if [ -f "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" ]; then
        BRAVE_PATH="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v brave-browser &> /dev/null; then
        BRAVE_PATH=$(which brave-browser)
    elif command -v brave &> /dev/null; then
        BRAVE_PATH=$(which brave)
    fi
fi

if [ -n "$BRAVE_PATH" ]; then
    echo "   Brave browser found: $BRAVE_PATH"
else
    echo ""
    echo -e "${YELLOW}[WARNING] Brave browser not found${NC}"
    echo ""
    echo "Please install Brave from: https://brave.com/download/"
    echo ""
    echo "You can continue setup, but the screenshot capture"
    echo "feature will not work until Brave is installed."
    echo ""
    read -p "Press Enter to continue..."
fi

# Step 5: Check configuration
echo ""
echo "[5/5] Checking configuration..."

if [ -f "config.json" ]; then
    echo "   Configuration file found: config.json"
else
    echo "   Creating default configuration file..."
    cat > config.json << EOF
{
    "api_key": "",
    "selected_model": "google/gemini-2.5-flash"
}
EOF
    echo "   Created: config.json"
    echo ""
    echo -e "${YELLOW}   [NOTE] Please add your OpenRouter API key in the Settings panel${NC}"
    echo "          after the application launches."
fi

# Make script executable (if run from another script)
chmod +x "$0" 2>/dev/null

# Launch application
echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "Launching Homework Helper AI..."
echo ""

# Suppress warnings for cleaner output
export TK_SILENCE_DEPRECATION=1
export PYTHONWARNINGS="ignore::urllib3.exceptions.NotOpenSSLWarning"

$PYTHON_CMD ui.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR] Application failed to start!${NC}"
    echo ""
    echo "Please check the error messages above."
    echo ""
    exit 1
fi
