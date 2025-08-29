# 📧 Email Notification Setup

This guide explains how to set up email notifications for your AutoPkg Runner.

## Option 1: Gmail (Recommended for Personal Use)

### Prerequisites
1. Gmail account
2. 2-Factor Authentication enabled
3. App-specific password

### Setup Steps

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Add GitHub Secrets**
   ```bash
   gh secret set EMAIL_USERNAME --body "your-email@gmail.com"
   gh secret set EMAIL_PASSWORD --body "your-app-password"
   gh secret set EMAIL_TO --body "recipient@example.com"
   ```

4. **Use Enhanced Workflow**
   - Rename `autopkg-mvp-enhanced.yml` to `autopkg-mvp.yml`
   - Or update your workflow to use the enhanced version

## Option 2: Office 365

### Setup Steps

1. **Get SMTP Settings**
   - Server: `smtp.office365.com`
   - Port: `587`
   - Security: STARTTLS

2. **Update Workflow**
   ```yaml
   - name: Send Email Report
     uses: dawidd6/action-send-mail@v3
     with:
       server_address: smtp.office365.com
       server_port: 587
       secure: true
       username: ${{ secrets.EMAIL_USERNAME }}
       password: ${{ secrets.EMAIL_PASSWORD }}
   ```

3. **Add Secrets**
   ```bash
   gh secret set EMAIL_USERNAME --body "your-email@company.com"
   gh secret set EMAIL_PASSWORD --body "your-password"
   gh secret set EMAIL_TO --body "team@company.com"
   ```

## Option 3: SendGrid (Professional)

### Setup Steps

1. **Create SendGrid Account**
   - Sign up at [SendGrid](https://sendgrid.com)
   - Get API key from Settings → API Keys

2. **Update Workflow**
   ```yaml
   - name: Send Email via SendGrid
     uses: peter-evans/sendgrid-action@v1
     with:
       sendgrid-api-key: ${{ secrets.SENDGRID_API_KEY }}
   ```

## Email Content Customization

### Basic Email
The default email includes:
- Run summary (success/failed counts)
- Link to GitHub Actions run
- Timestamp and run number

### Custom HTML Email
For richer emails, modify the workflow:

```yaml
- name: Send HTML Email
  uses: dawidd6/action-send-mail@v3
  with:
    subject: AutoPkg Report - ${{ needs.process-and-upload.outputs.success_count }} Successful
    html_body: file://reports/report.html
    attachments: reports/report.html
```

## Email Triggers

### When Emails Are Sent

1. **Scheduled Runs**: Always
2. **Manual Runs**: Optional (checkbox)
3. **Failures**: Always (separate notification)

### Customizing Triggers

Edit the `if` condition in the workflow:

```yaml
# Only on failure
if: failure()

# Only on success
if: success()

# Always
if: always()

# Only for scheduled runs
if: github.event_name == 'schedule'
```

## Multiple Recipients

Add multiple recipients separated by commas:

```bash
gh secret set EMAIL_TO --body "admin@company.com,team@company.com,manager@company.com"
```

## Testing Email Setup

1. **Test Locally First**
   ```bash
   # Test SMTP connection
   python3 -c "
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   server.quit()
   print('Success!')
   "
   ```

2. **Test with GitHub Actions**
   - Run workflow manually
   - Check "Send email notification"
   - Verify email received

## Troubleshooting

### Gmail Issues
- **Authentication Failed**: Regenerate app password
- **Less Secure Apps**: Not needed with app passwords
- **Blocked Sign-in**: Check Google security alerts

### Office 365 Issues
- **MFA Required**: Use app password
- **IP Blocking**: Whitelist GitHub Actions IPs
- **Tenant Restrictions**: Check with IT admin

### No Emails Received
1. Check spam folder
2. Verify secrets are set correctly
3. Check workflow logs for errors
4. Test SMTP connection locally

## Email Templates

### Success Template
```
Subject: ✅ AutoPkg Success - All {count} Apps Updated

All packages processed successfully!
- Chrome: ✅ Updated
- Firefox: ✅ Updated  
- Zoom: ✅ Updated

View details: {workflow_url}
```

### Failure Template
```
Subject: ⚠️ AutoPkg Failed - {failed_count} Apps Need Attention

Some packages failed processing:
- Chrome: ❌ Hash mismatch
- Firefox: ✅ Success
- Zoom: ❌ Download failed

Action required: {workflow_url}
```

## Best Practices

1. **Use App Passwords**: Never use your main password
2. **Limit Recipients**: Keep distribution list small
3. **Archive Reports**: Set up email filters/labels
4. **Monitor Frequency**: Avoid email fatigue
5. **Test Changes**: Always test email changes first

## Alternative: GitHub Notifications

If you prefer not to use email, GitHub provides built-in notifications:

1. **Watch the Repository**
   - Click "Watch" → "Custom"
   - Select "Actions"

2. **GitHub Mobile App**
   - Get push notifications
   - View run summaries

3. **GitHub CLI**
   ```bash
   # Check latest run
   gh run list --limit 1
   
   # Watch a run
   gh run watch
   ```

---

Remember: Email notifications are optional. The GitHub Actions summary and artifacts provide all the same information.