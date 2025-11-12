#!/bin/bash
# Error Reporting Server Setup Script
# Run this on your server (Raspberry Pi, VPS, etc.) to set up the error reporting API

set -e

echo "===================================="
echo "Error Reporting Server Setup"
echo "===================================="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python $(python3 --version) detected"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run server: python error_server.py"
echo "  3. For production: gunicorn -w 4 -b 0.0.0.0:5000 error_server:app"
echo ""
echo "The server will be accessible at http://localhost:5000"
echo ""
echo "Next steps:"
echo "  - Set up Cloudflare Tunnel for external access (see docs/DOMAIN_SETUP.md)"
echo "  - Update config.json with your server URL"
echo ""
