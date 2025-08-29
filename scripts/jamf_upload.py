#!/usr/bin/env python3
"""
MVP AutoPkg Runner - Jamf Upload Script
Uploads validated packages to Jamf Pro
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

class JamfUploader:
    def __init__(self):
        # Get Jamf credentials from environment
        self.jamf_url = os.environ.get('JAMF_URL', '').rstrip('/')
        self.username = os.environ.get('JAMF_USERNAME')
        self.password = os.environ.get('JAMF_PASSWORD')
        
        # Validate credentials
        if not all([self.jamf_url, self.username, self.password]):
            print("❌ Error: Missing Jamf credentials in environment variables")
            print("   Required: JAMF_URL, JAMF_USERNAME, JAMF_PASSWORD")
            sys.exit(1)
        
        # Paths
        self.reports_dir = Path(__file__).parent.parent / 'reports'
        self.downloads_dir = Path(__file__).parent.parent / 'downloads'
        
        # API token (will be obtained during authentication)
        self.token = None
        
    def authenticate(self):
        """Authenticate with Jamf Pro and get API token"""
        print("🔐 Authenticating with Jamf Pro...")
        
        # Get token using basic auth
        auth_url = f"{self.jamf_url}/api/v1/auth/token"
        
        try:
            response = requests.post(
                auth_url,
                auth=(self.username, self.password),
                timeout=30
            )
            
            if response.status_code == 200:
                self.token = response.json()['token']
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def upload_package(self, filepath, app_name, category="Testing"):
        """Upload a package to Jamf Pro"""
        if not self.token:
            print("❌ Not authenticated")
            return False
        
        print(f"\n📤 Uploading {app_name} to Jamf Pro...")
        
        # Check if package already exists
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # First, check if package exists
        packages_url = f"{self.jamf_url}/JSSResource/packages/name/{app_name}"
        
        try:
            check_response = requests.get(
                packages_url,
                headers={'Authorization': f'Bearer {self.token}', 'Accept': 'application/json'},
                timeout=30
            )
            
            package_exists = check_response.status_code == 200
            
            if package_exists:
                print(f"   Package '{app_name}' already exists, will update...")
                # Get package ID for update
                package_data = check_response.json()
                package_id = package_data.get('package', {}).get('id')
            else:
                print(f"   Creating new package '{app_name}'...")
                package_id = None
                
        except Exception as e:
            print(f"   Warning: Could not check existing package: {str(e)}")
            package_id = None
        
        # Prepare package metadata
        package_metadata = {
            'name': app_name,
            'category': category,
            'filename': Path(filepath).name,
            'info': f'Uploaded by AutoPkg MVP on {datetime.now().isoformat()}',
            'notes': 'Automated package upload via AutoPkg MVP Runner',
            'priority': 10,
            'reboot_required': False,
            'fill_user_template': False,
            'fill_existing_users': False,
            'os_requirements': '',
            'swu': False,
            'self_heal_notify': False,
            'os_install': False,
            'suppress_updates': False,
            'suppress_from_dock': False,
            'suppress_eula': False,
            'suppress_registration': False
        }
        
        # Create or update package record
        if package_id:
            # Update existing package
            api_url = f"{self.jamf_url}/JSSResource/packages/id/{package_id}"
            method = 'PUT'
        else:
            # Create new package
            api_url = f"{self.jamf_url}/JSSResource/packages/id/0"
            method = 'POST'
        
        # Create XML payload
        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<package>
    <name>{package_metadata['name']}</name>
    <category>{package_metadata['category']}</category>
    <filename>{package_metadata['filename']}</filename>
    <info>{package_metadata['info']}</info>
    <notes>{package_metadata['notes']}</notes>
    <priority>{package_metadata['priority']}</priority>
    <reboot_required>{str(package_metadata['reboot_required']).lower()}</reboot_required>
    <fill_user_template>{str(package_metadata['fill_user_template']).lower()}</fill_user_template>
    <fill_existing_users>{str(package_metadata['fill_existing_users']).lower()}</fill_existing_users>
    <os_requirements>{package_metadata['os_requirements']}</os_requirements>
</package>"""
        
        try:
            # Create/update package record
            response = requests.request(
                method,
                api_url,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/xml'
                },
                data=xml_data,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Package record {'updated' if package_id else 'created'} successfully")
                
                # Parse response to get package ID if newly created
                if not package_id and response.text:
                    try:
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(response.text)
                        package_id = root.find('.//id')
                        if package_id is not None:
                            package_id = package_id.text
                    except:
                        pass
                
                # Now upload the actual package file
                print(f"   📦 Uploading package file ({Path(filepath).stat().st_size / 1024 / 1024:.2f} MB)...")
                
                # For Jamf Cloud, use the file upload endpoint
                upload_url = f"{self.jamf_url}/api/v1/packages/{package_id or app_name}/upload"
                
                with open(filepath, 'rb') as f:
                    files = {'file': (Path(filepath).name, f, 'application/octet-stream')}
                    
                    upload_response = requests.post(
                        upload_url,
                        headers={'Authorization': f'Bearer {self.token}'},
                        files=files,
                        timeout=600  # 10 minutes for large files
                    )
                    
                    if upload_response.status_code in [200, 201]:
                        print(f"   ✅ Package file uploaded successfully")
                        return True
                    else:
                        # Try legacy upload method
                        print(f"   ⚠️  New upload method failed, trying legacy method...")
                        
                        # Legacy file upload via JSSResource
                        legacy_url = f"{self.jamf_url}/JSSResource/fileuploads/packages/id/{package_id or 0}"
                        
                        with open(filepath, 'rb') as f2:
                            files2 = {'file': f2}
                            legacy_response = requests.post(
                                legacy_url,
                                headers={'Authorization': f'Bearer {self.token}'},
                                files=files2,
                                timeout=600
                            )
                            
                            if legacy_response.status_code in [200, 201]:
                                print(f"   ✅ Package file uploaded successfully (legacy method)")
                                return True
                            else:
                                print(f"   ❌ Failed to upload package file: {legacy_response.status_code}")
                                return False
            else:
                print(f"   ❌ Failed to create/update package record: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ❌ Upload timeout - file may be too large")
            return False
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Upload error: {str(e)}")
            return False
    
    def upload_all(self):
        """Upload all successfully validated packages"""
        print("=" * 60)
        print("Jamf Pro Package Uploader")
        print(f"Target: {self.jamf_url}")
        print("=" * 60)
        
        # Load validation results
        results_file = self.reports_dir / 'results.json'
        
        if not results_file.exists():
            print("❌ No results.json file found. Run download_and_validate.py first.")
            sys.exit(1)
        
        with open(results_file) as f:
            results = json.load(f)
        
        # Authenticate
        if not self.authenticate():
            print("❌ Failed to authenticate with Jamf Pro")
            sys.exit(1)
        
        # Process each app
        upload_results = []
        
        for app in results.get('apps', []):
            if app.get('status') == 'success' and app.get('path'):
                filepath = Path(app['path'])
                
                if filepath.exists():
                    success = self.upload_package(
                        filepath,
                        app['name'],
                        category="Testing"
                    )
                    
                    upload_results.append({
                        'name': app['name'],
                        'uploaded': success
                    })
                else:
                    print(f"⚠️  Package file not found: {filepath}")
                    upload_results.append({
                        'name': app['name'],
                        'uploaded': False,
                        'error': 'File not found'
                    })
            else:
                print(f"⏭️  Skipping {app.get('name', 'unknown')} - validation failed")
        
        # Print summary
        print("\n" + "=" * 60)
        print("UPLOAD SUMMARY")
        print("=" * 60)
        
        success_count = sum(1 for r in upload_results if r.get('uploaded'))
        failed_count = sum(1 for r in upload_results if not r.get('uploaded'))
        
        print(f"✅ Uploaded: {success_count}")
        print(f"❌ Failed: {failed_count}")
        
        # Save upload results
        upload_report = {
            'timestamp': datetime.now().isoformat(),
            'jamf_url': self.jamf_url,
            'results': upload_results
        }
        
        upload_report_file = self.reports_dir / f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(upload_report_file, 'w') as f:
            json.dump(upload_report, f, indent=2)
        
        print(f"📄 Upload report saved: {upload_report_file}")
        
        # Exit with error if any failed
        if failed_count > 0:
            sys.exit(1)
        
        return upload_results

if __name__ == '__main__':
    uploader = JamfUploader()
    uploader.upload_all()