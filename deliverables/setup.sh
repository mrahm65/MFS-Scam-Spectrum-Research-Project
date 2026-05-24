#!/bin/bash
# One-command setup for MFS Scam Research Data Collection Toolkit
# Usage: chmod +x setup.sh && ./setup.sh

set -e

echo "========================================"
echo "MFS Scam Research - Setup"
echo "========================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "[+] Python version: $python_version"

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install core dependencies
echo "[+] Installing core dependencies..."
pip install -q google-play-scraper pandas numpy requests dnspython 2>&1 | tail -1

# Install optional dependencies
echo "[+] Installing optional dependencies..."
pip install -q presidio-analyzer presidio-anonymizer 2>&1 | tail -1 || echo "    [!] Presidio optional, skipping"

# Create output directories
echo "[+] Setting up directories..."
mkdir -p {stream_a_datasets,stream_e_app_reviews,stream_c_phishing_urls,data_pipeline,survey_form,annotation_interface,infrastructure_monitoring,deliverables}

# Verify installations
echo "[+] Verifying installations..."
python3 -c "import google_play_scraper; print('    google-play-scraper: OK')" 2>/dev/null || echo "    google-play-scraper: MISSING"
python3 -c "import pandas; print('    pandas: OK')" 2>/dev/null || echo "    pandas: MISSING"
python3 -c "import requests; print('    requests: OK')" 2>/dev/null || echo "    requests: MISSING"
python3 -c "import dns; print('    dnspython: OK')" 2>/dev/null || echo "    dnspython: MISSING"
python3 -c "import presidio_analyzer; print('    presidio: OK')" 2>/dev/null || echo "    presidio: optional, not installed"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Download Mendeley dataset:"
echo "     cd stream_a_datasets && python download_mendeley_dataset.py --manual"
echo ""
echo "  2. Collect app reviews:"
echo "     python stream_e_app_reviews/app_review_scraper.py --all --count 5000"
echo ""
echo "  3. Start phishing URL collection:"
echo "     python stream_c_phishing_urls/phishing_pipeline.py --refresh-all --enrich"
echo ""
echo "  4. Generate survey form:"
echo "     python survey_form/survey_toolkit.py --generate"
echo ""
echo "  5. Launch annotation interface:"
echo "     python annotation_interface/annotation_tool.py --setup"
echo ""
