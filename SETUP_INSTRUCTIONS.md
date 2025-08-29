# 🚀 Setup Instructions - Cloud AutoPkg Runner

## ✅ Completed Steps

1. **MVP Code Implementation** - DONE ✅
   - All scripts created and tested
   - Configuration files ready
   - Documentation complete
   - 6 enterprise apps configured

2. **Enhanced Security** - DONE ✅
   - Team ID signature verification implemented
   - DMG to PKG conversion added
   - Code signature verification using Apple tools

3. **Local Testing** - DONE ✅
   - Downloaded all 6 packages successfully
   - Signature verification tested with Team IDs
   - No need to update hashes (Team IDs don't change)

4. **GitHub Repository** - DONE ✅
   - Repository created at https://github.com/vivesm/cloud-autopkg-runner
   - Code pushed and tested

## 📋 Next Steps to Complete

### Step 1: Add GitHub Secrets ⚠️ REQUIRED

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
2. ✅ All 6 apps show "success" in summary
3. ✅ Code signatures verified with Team IDs
4. ✅ DMG files auto-converted to PKG
5. ✅ Artifacts contain reports and packages
6. ✅ Email received (if configured)
7. ✅ Packages appear in Jamf Pro

## 🐛 Troubleshooting

### Common Issues:

**"Authentication failed" in Jamf upload**
- Check JAMF_URL has no trailing slash
- Verify username/password are correct
- Ensure API user has package upload permissions

**"Signature verification failed" errors**
- Team ID might have changed (very rare)
- Check signature with: `python3 scripts/verify_signature.py <package_file>`
- Update Team ID in `config/apps.json` if needed

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