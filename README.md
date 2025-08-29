# 🚀 Cloud AutoPkg Runner - MVP

A lightweight, cost-effective automation pipeline for downloading, validating, and deploying macOS application packages to Jamf Pro using GitHub Actions.

## ✨ Features

- **🤖 Automated Downloads**: Direct downloads of 6 enterprise macOS applications
- **🔐 Code Signature Verification**: Team ID verification using Apple Developer certificates
- **🔒 Security Scanning**: Optional VirusTotal malware scanning
- **📦 Format Conversion**: Automatic DMG to PKG conversion for Jamf compatibility
- **☁️ Jamf Pro Integration**: Automatic upload to your Jamf Pro server
- **💰 Cost Effective**: Runs on Ubuntu ($0.008/minute) instead of macOS ($0.08/minute)
- **📊 Detailed Reporting**: JSON reports and GitHub Actions summaries
- **🔧 Local Testing**: Test the entire pipeline locally before deployment

## 🎯 MVP Scope

This MVP implementation includes:
- **6 enterprise applications**: 
  - Google Chrome
  - Mozilla Firefox
  - Zoom
  - 1Password 8
  - Jamf Connect
  - Okta Verify
- **Team ID verification** (more reliable than SHA256 - doesn't change between versions)
- **DMG to PKG conversion** for apps distributed as disk images
- **Simple Jamf Pro upload** with automatic format handling
- **Daily automated runs** via GitHub Actions

## 📋 Prerequisites

- GitHub account with Actions enabled
- Jamf Pro instance with API access
- VirusTotal API key (free tier)
- Python 3.11+

## 🚀 Quick Start

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/cloud-autopkg-runner.git
cd cloud-autopkg-runner
```

### 2. Configure Secrets

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

```bash
VIRUSTOTAL_API_KEY=your_virustotal_api_key
JAMF_URL=https://your-instance.jamfcloud.com
JAMF_USERNAME=your_api_username
JAMF_PASSWORD=your_api_password
```

### 3. Configuration

The pipeline uses Team ID verification by default, which is more reliable than SHA256 hashes since Team IDs don't change between app versions. 

Check `config/apps.json` to see the configured apps and their Team IDs.

### 4. Test Locally

```bash
# Full test with all features
export VIRUSTOTAL_API_KEY="your_virustotal_api_key"
export JAMF_URL="https://your-instance.jamfcloud.com"
export JAMF_USERNAME="your_username"
export JAMF_PASSWORD="your_password"

./test_local.sh
```

### 5. Deploy to GitHub Actions

```bash
git add .
git commit -m "Initial MVP setup"
git push origin main
```

Then trigger manually:
- Go to Actions tab in GitHub
- Select "AutoPkg MVP Runner"
- Click "Run workflow"

## 📁 Project Structure

```
cloud-autopkg-runner/
├── .github/
│   └── workflows/
│       └── autopkg-mvp.yml          # GitHub Actions workflow
├── scripts/
│   ├── download_and_validate.py     # Download & signature verification
│   ├── jamf_upload.py              # Jamf Pro upload
│   ├── verify_signature.py         # Team ID verification
│   ├── dmg_to_pkg.py              # DMG to PKG converter
│   └── extract_pkg_from_dmg.py    # Extract PKG from DMG
├── config/
│   └── apps.json                   # Application configurations
├── reference/
│   └── Installomator.sh           # Reference for 700+ app configs
├── downloads/                       # Downloaded packages (git-ignored)
├── reports/                        # Processing reports
├── test_local.sh                   # Local testing script
├── FUTURE_FEATURES.md             # Roadmap and ideas
└── README.md                       # This file
```

## 🔧 Configuration

### apps.json

Configure applications in `config/apps.json`:

```json
{
  "apps": [
    {
      "name": "GoogleChrome",
      "filename": "GoogleChrome.pkg",
      "url": "https://dl.google.com/chrome/...",
      "team_id": "EQHXZ8M8AV",
      "notes": "Uses Team ID verification instead of SHA256"
    },
    {
      "name": "JamfConnect",
      "filename": "JamfConnect.dmg",
      "url": "https://files.jamfconnect.com/JamfConnect.dmg",
      "team_id": "483DWKW443",
      "type": "pkgInDmg",
      "notes": "PKG will be extracted from DMG"
    }
  ]
}
```

**Key Configuration Options:**
- `team_id`: Apple Developer Team ID for signature verification (preferred)
- `sha256`: SHA256 hash for verification (fallback if no team_id)
- `type`: Package type (`pkg`, `dmg`, `pkgInDmg`)

### Workflow Schedule

Edit `.github/workflows/autopkg-mvp.yml` to change the schedule:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

## 🧪 Testing

### Local Testing Options

```bash
# Test everything
./test_local.sh

# Skip download (use existing files)
./test_local.sh --skip-download

# Skip upload (download and validate only)
./test_local.sh --skip-upload

# Test specific app
./test_local.sh --app GoogleChrome
```

### Manual GitHub Actions Run

1. Go to Actions tab
2. Select "AutoPkg MVP Runner"
3. Click "Run workflow"
4. Optional: Check "Skip Jamf upload" for test mode

## 📊 Reports

Reports are generated in JSON format and saved to `reports/`:

- `results.json` - Latest run results
- `results_YYYYMMDD_HHMMSS.json` - Timestamped results
- `upload_YYYYMMDD_HHMMSS.json` - Upload results

Example report structure:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "apps": [
    {
      "name": "GoogleChrome",
      "status": "success",
      "size_mb": 234.5,
      "virustotal": {
        "malicious": 0,
        "harmless": 72
      }
    }
  ]
}
```

## 🔒 Security

This MVP includes multiple security layers:

1. **HTTPS Downloads** - All packages downloaded over TLS
2. **SHA256 Verification** - Ensures package integrity
3. **VirusTotal Scanning** - Checks against 70+ antivirus engines
4. **Secure Secrets** - GitHub encrypted secrets for credentials

## 💰 Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| GitHub Actions (Ubuntu) | ~$0.04/run | 5 minutes @ $0.008/min |
| VirusTotal API | Free | 500 requests/day |
| **Monthly Total** | ~$1.20 | 30 daily runs |

Compare to macOS runners: ~$12/month (10x more expensive)

## 🚦 Monitoring

### GitHub Actions Dashboard
- View run history
- Check logs for each step
- Download artifacts (packages & reports)

### Email Notifications
GitHub Actions sends email notifications for:
- Failed scheduled runs
- Manual run completions

### Automated Issues
Failed scheduled runs create GitHub issues automatically

## 🐛 Troubleshooting

### Common Issues

**VirusTotal API Rate Limiting**
- Free tier: 4 requests/minute
- Solution: Runs are spaced out automatically

**Package Download Fails**
- Check if URL has changed
- Verify network connectivity
- Update URL in `config/apps.json`

**Hash Mismatch**
- Package was updated
- Run locally to get new hash
- Update `config/apps.json`

**Jamf Upload Fails**
- Verify API credentials
- Check API user permissions
- Ensure Jamf Pro is accessible

### Debug Mode

Run locally with verbose output:
```bash
python3 scripts/download_and_validate.py
python3 scripts/jamf_upload.py
```

## 📈 Next Steps

After MVP success, consider adding:

- **Phase 2**: More applications (10+)
- **Phase 3**: AutoPkg recipe integration
- **Phase 4**: Code signature verification (requires macOS runner)
- **Phase 5**: Slack/Teams notifications
- **Phase 6**: Web dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- AutoPkg community for inspiration
- Jamf Pro for API documentation
- VirusTotal for malware scanning API

## 💬 Support

- Create an issue for bugs/features
- Check existing issues for solutions
- Review workflow logs for debugging

---

**Version**: 1.0.0-MVP  
**Last Updated**: January 2024  
**Status**: Production Ready 🟢