# 🚀 Setup Instructions - Cloud AutoPkg Runner

## ✅ Completed Steps

1. **MVP Code Implementation** - DONE ✅
   - All scripts created and tested
   - Configuration files ready
   - Documentation complete

2. **Local Testing** - DONE ✅
   - Downloaded all packages successfully
   - SHA256 hashes verified
   - Configuration updated with correct hashes

## 📋 Next Steps to Complete

### Step 1: Create GitHub Repository

#### Option A: Using GitHub Web Interface
1. Go to https://github.com/new
2. Repository name: `cloud-autopkg-runner`
3. Description: `Automated macOS application patching pipeline for Jamf Pro using GitHub Actions`
4. Make it Public
5. DON'T initialize with README (we already have one)
6. Click "Create repository"

#### Option B: Using GitHub CLI (if installed)
```bash
# Install GitHub CLI if needed
brew install gh

# Authenticate
gh auth login

# Create repo and push
gh repo create cloud-autopkg-runner --public \
  --description "Automated macOS application patching pipeline for Jamf Pro using GitHub Actions" \
  --push --source=.
```

### Step 2: Push Code to GitHub

After creating the repository on GitHub:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/cloud-autopkg-runner.git

# Push code
git branch -M main
git push -u origin main
```

### Step 3: Add GitHub Secrets

Go to your repository on GitHub:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

#### Required Secrets:

**VIRUSTOTAL_API_KEY** (Optional but recommended)
- Get free API key from https://www.virustotal.com
- Sign up → API Key section
- Copy the key

**JAMF_URL** (Required for upload)
- Example: `https://yourcompany.jamfcloud.com`
- NO trailing slash

**JAMF_USERNAME** (Required for upload)
- Your Jamf Pro API username
- Needs package upload permissions

**JAMF_PASSWORD** (Required for upload)
- Your Jamf Pro API password

#### Optional Email Secrets (for notifications):

**EMAIL_USERNAME**
- Gmail: `your-email@gmail.com`

**EMAIL_PASSWORD**  
- Gmail: Use app password (not regular password)
- Get it from: https://myaccount.google.com/apppasswords

**EMAIL_TO**
- Recipient email: `team@company.com`

### Step 4: Test GitHub Actions

#### Manual Test Run:
1. Go to **Actions** tab in your repository
2. Select **"AutoPkg MVP Runner"** workflow
3. Click **"Run workflow"**
4. Options:
   - Check "Skip Jamf upload" for test mode
   - Leave unchecked for full run
5. Click **"Run workflow"** button

#### Monitor the Run:
1. Click on the running workflow
2. Watch real-time logs
3. Download artifacts when complete
4. Check email if configured

### Step 5: Enable Scheduled Runs

The workflow is already configured to run daily at 2 AM UTC.
To change the schedule, edit `.github/workflows/autopkg-mvp.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

Cron examples:
- `0 2 * * *` - Daily at 2 AM UTC
- `0 */6 * * *` - Every 6 hours
- `0 2 * * 1-5` - Weekdays only at 2 AM UTC

## 🎯 Quick Test Commands

```bash
# Test locally first (no upload)
./test_local.sh --skip-upload

# Test with VirusTotal
export VIRUSTOTAL_API_KEY="your-key"
./test_local.sh --skip-upload

# Full local test (with Jamf)
export JAMF_URL="https://yourcompany.jamfcloud.com"
export JAMF_USERNAME="api-user"
export JAMF_PASSWORD="api-password"
./test_local.sh
```

## ✨ Success Indicators

You'll know it's working when:
1. ✅ GitHub Actions shows green checkmark
2. ✅ All 3 apps show "success" in summary
3. ✅ Artifacts contain reports and packages
4. ✅ Email received (if configured)
5. ✅ Packages appear in Jamf Pro

## 🐛 Troubleshooting

### Common Issues:

**"Authentication failed" in Jamf upload**
- Check JAMF_URL has no trailing slash
- Verify username/password are correct
- Ensure API user has package upload permissions

**"Hash mismatch" errors**
- Apps were updated by vendor
- Re-run local test to get new hashes
- Update `config/apps.json`

**"VirusTotal timeout"**
- Free tier rate limit (4/minute)
- Normal for first run
- Will use cache on subsequent runs

**No email received**
- Check spam folder
- Verify app password (not regular password)
- Check EMAIL_TO address is correct

## 📊 What's Next?

After successful MVP deployment:

### Week 1: Monitor & Stabilize
- Watch daily runs
- Check success rates
- Fix any issues

### Week 2: Add More Apps
- Slack
- Microsoft Teams  
- Visual Studio Code
- 1Password

### Week 3: Enhance Features
- HTML reports
- Better notifications
- Version tracking

### Week 4: Production Ready
- Documentation updates
- Team training
- Rollout plan

## 💬 Support

- Check workflow logs in GitHub Actions
- Review this documentation
- Create issues in the repository for bugs

---

**Current Status**: Ready to push to GitHub! 🚀

Follow Steps 1-5 above to complete deployment.