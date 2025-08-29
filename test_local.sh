#!/bin/bash

# AutoPkg MVP Runner - Local Testing Script
# This script allows you to test the pipeline locally before deploying to GitHub Actions

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    AutoPkg MVP Runner - Local Testing     ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if running from correct directory
if [ ! -f "config/apps.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Parse command line arguments
SKIP_DOWNLOAD=false
SKIP_UPLOAD=false
SPECIFIC_APP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-download)
            SKIP_DOWNLOAD=true
            shift
            ;;
        --skip-upload)
            SKIP_UPLOAD=true
            shift
            ;;
        --app)
            SPECIFIC_APP="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --skip-download    Skip download and validation phase"
            echo "  --skip-upload      Skip Jamf upload phase"
            echo "  --app NAME         Process specific app only"
            echo "  --help            Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  VIRUSTOTAL_API_KEY    VirusTotal API key (optional)"
            echo "  JAMF_URL             Jamf Pro URL (required for upload)"
            echo "  JAMF_USERNAME        Jamf Pro username (required for upload)"
            echo "  JAMF_PASSWORD        Jamf Pro password (required for upload)"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check for required environment variables
print_info "Checking environment variables..."

if [ -n "$VIRUSTOTAL_API_KEY" ]; then
    print_success "VirusTotal API key configured"
else
    print_warning "VirusTotal API key not set (scans will be skipped)"
fi

if [ "$SKIP_UPLOAD" = false ]; then
    if [ -z "$JAMF_URL" ] || [ -z "$JAMF_USERNAME" ] || [ -z "$JAMF_PASSWORD" ]; then
        print_warning "Jamf credentials not fully configured"
        print_info "Set JAMF_URL, JAMF_USERNAME, and JAMF_PASSWORD to enable upload"
        print_info "Or use --skip-upload to skip the upload phase"
        read -p "Continue without Jamf upload? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        SKIP_UPLOAD=true
    else
        print_success "Jamf credentials configured"
        print_info "Target: $JAMF_URL"
    fi
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
pip3 install -q requests pyyaml 2>/dev/null || {
    print_warning "Could not install dependencies with pip3, trying pip..."
    pip install -q requests pyyaml
}
print_success "Dependencies installed"

# Create required directories
print_info "Creating required directories..."
mkdir -p downloads reports
print_success "Directories ready"

# Phase 1: Download and Validation
if [ "$SKIP_DOWNLOAD" = false ]; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Phase 1: Download and Validation     ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    if [ -n "$SPECIFIC_APP" ]; then
        print_info "Processing specific app: $SPECIFIC_APP"
    fi
    
    if python3 scripts/download_and_validate.py; then
        print_success "Download and validation completed successfully"
    else
        print_error "Download and validation failed"
        exit 1
    fi
else
    print_info "Skipping download phase (--skip-download flag)"
fi

# Phase 2: Jamf Upload
if [ "$SKIP_UPLOAD" = false ] && [ -f "reports/results.json" ]; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}        Phase 2: Jamf Upload            ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    if python3 scripts/jamf_upload.py; then
        print_success "Jamf upload completed successfully"
    else
        print_error "Jamf upload failed"
        exit 1
    fi
else
    if [ "$SKIP_UPLOAD" = true ]; then
        print_info "Skipping upload phase (--skip-upload flag or missing credentials)"
    else
        print_warning "No results.json found, skipping upload"
    fi
fi

# Display results
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}           Test Results                 ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ -f "reports/results.json" ]; then
    print_info "Processing results:"
    
    # Use Python to parse JSON since jq might not be installed
    python3 -c "
import json
import sys

with open('reports/results.json') as f:
    data = json.load(f)
    
print('Timestamp:', data.get('timestamp', 'N/A'))
print('')
print('Apps processed:')

for app in data.get('apps', []):
    status = '✅' if app.get('status') == 'success' else '❌'
    name = app.get('name', 'Unknown')
    
    print(f'  {status} {name}')
    
    if app.get('status') == 'success':
        if 'size_mb' in app:
            print(f'     Size: {app[\"size_mb\"]} MB')
        if 'virustotal' in app and not app['virustotal'].get('skipped'):
            vt = app['virustotal']
            print(f'     VirusTotal: {vt.get(\"malicious\", 0)} malicious, {vt.get(\"harmless\", 0)} harmless')
    else:
        if 'error' in app:
            print(f'     Error: {app[\"error\"]}')

# Summary
success_count = sum(1 for app in data.get('apps', []) if app.get('status') == 'success')
total_count = len(data.get('apps', []))

print('')
print(f'Summary: {success_count}/{total_count} successful')
"
    
    echo ""
    print_info "Full results saved in: reports/results.json"
    
    # List downloaded files
    if [ -d "downloads" ] && [ "$(ls -A downloads)" ]; then
        print_info "Downloaded files:"
        ls -lh downloads/ | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}'
    fi
else
    print_warning "No results file found"
fi

echo ""
print_success "Local testing completed!"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review the results above"
echo "2. Update SHA256 hashes in config/apps.json if needed"
echo "3. Commit changes to Git"
echo "4. Push to GitHub and run the workflow"
echo ""