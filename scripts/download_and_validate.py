#!/usr/bin/env python3
"""
MVP AutoPkg Runner - Download and Validate Script
Downloads packages, verifies hashes, and scans with VirusTotal
"""

import json
import hashlib
import requests
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile
import shutil

class MVPProcessor:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / 'config' / 'apps.json'
        self.downloads = Path(__file__).parent.parent / 'downloads'
        self.reports = Path(__file__).parent.parent / 'reports'
        
        # Create directories
        self.downloads.mkdir(exist_ok=True)
        self.reports.mkdir(exist_ok=True)
        
        # Load configuration
        with open(self.config_path) as f:
            self.config = json.load(f)
        
        # VirusTotal API key (optional for MVP)
        self.vt_api_key = os.environ.get('VIRUSTOTAL_API_KEY')
        
    def process_all(self):
        """Process all configured applications"""
        print("=" * 60)
        print("AutoPkg MVP Runner - Starting Processing")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'apps': []
        }
        
        for app in self.config['apps']:
            print(f"\n📦 Processing {app['name']}...")
            app_result = {
                'name': app['name'],
                'version': app.get('version', 'latest'),
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                # Set current app type for download processing
                self.current_app_type = app.get('type', 'pkg')
                
                # Step 1: Download
                print(f"  ⬇️  Downloading {app['filename']}...")
                filepath = self.download(app['url'], app['filename'])
                app_result['download'] = 'success'
                app_result['path'] = str(filepath)
                app_result['size_mb'] = round(filepath.stat().st_size / 1024 / 1024, 2)
                
                # Step 2: Verify package integrity
                # Prefer Team ID verification over SHA256 if available
                if app.get('team_id'):
                    print(f"  🔐 Verifying code signature with Team ID...")
                    if self.verify_signature(filepath, app['team_id']):
                        print(f"  ✅ Signature verified with Team ID: {app['team_id']}")
                        app_result['signature_verification'] = 'success'
                        app_result['team_id'] = app['team_id']
                    else:
                        raise Exception(f"Signature verification failed for Team ID: {app['team_id']}")
                elif app.get('sha256') and app['sha256'] != 'WILL_BE_DIFFERENT_AFTER_CONVERSION':
                    print(f"  🔐 Verifying SHA256 hash...")
                    actual_hash = self.calculate_hash(filepath)
                    
                    if actual_hash == app['sha256']:
                        print(f"  ✅ Hash verified: {actual_hash[:16]}...")
                        app_result['hash_verification'] = 'success'
                    else:
                        raise Exception(f"Hash mismatch! Expected: {app['sha256'][:16]}..., Got: {actual_hash[:16]}...")
                else:
                    print(f"  ⚠️  No verification configured (no team_id or sha256)")
                    actual_hash = self.calculate_hash(filepath)
                    app_result['hash_verification'] = 'skipped'
                    app_result['actual_hash'] = actual_hash
                    print(f"     Actual hash: {actual_hash}")
                
                # Step 3: VirusTotal scan
                if self.vt_api_key:
                    print(f"  🔍 Scanning with VirusTotal...")
                    vt_results = self.scan_virustotal(filepath, actual_hash)
                    app_result['virustotal'] = vt_results
                    
                    if vt_results.get('malicious', 0) > 5:
                        raise Exception(f"VirusTotal detected malware: {vt_results['malicious']} engines")
                    
                    print(f"  ✅ VirusTotal scan clean: {vt_results.get('malicious', 0)} malicious, {vt_results.get('harmless', 0)} harmless")
                else:
                    print(f"  ⚠️  VirusTotal API key not configured, skipping scan")
                    app_result['virustotal'] = {'skipped': True}
                
                app_result['status'] = 'success'
                print(f"  ✅ {app['name']} processing complete!")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                app_result['status'] = 'failed'
                app_result['error'] = str(e)
            
            results['apps'].append(app_result)
        
        # Save results
        report_file = self.reports / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Also save as latest for easy access
        latest_file = self.reports / 'results.json'
        with open(latest_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        success_count = sum(1 for app in results['apps'] if app['status'] == 'success')
        failed_count = sum(1 for app in results['apps'] if app['status'] == 'failed')
        
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📄 Report saved: {report_file}")
        
        # Exit with error if any failed
        if failed_count > 0:
            sys.exit(1)
        
        return results
            
    def download(self, url, filename):
        """Download a file from URL"""
        filepath = self.downloads / filename
        
        # Skip if already downloaded
        if filepath.exists():
            print(f"    File already exists, skipping download")
            return filepath
        
        response = requests.get(url, stream=True, allow_redirects=True, timeout=300)
        response.raise_for_status()
        
        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress
        downloaded = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"    Progress: {percent:.1f}%", end='\r')
        
        print(f"    Downloaded: {filepath.name} ({round(filepath.stat().st_size / 1024 / 1024, 2)} MB)")
        
        # Handle different package types
        if str(filepath).lower().endswith('.dmg'):
            # Check if this is a pkgInDmg type (like Jamf Connect)
            if hasattr(self, 'current_app_type') and self.current_app_type == 'pkgInDmg':
                pkg_path = self.extract_pkg_from_dmg(filepath)
                if pkg_path:
                    return pkg_path
                else:
                    print(f"    ⚠️  PKG extraction from DMG failed")
            else:
                # Regular DMG - convert to PKG
                pkg_path = self.convert_dmg_to_pkg(filepath)
                if pkg_path:
                    return pkg_path
                else:
                    print(f"    ⚠️  DMG to PKG conversion failed, keeping DMG")
        
        return filepath
    
    def extract_pkg_from_dmg(self, dmg_path):
        """Extract PKG from DMG (for apps like Jamf Connect)"""
        print(f"  📦 Extracting PKG from DMG...")
        
        try:
            extractor_script = Path(__file__).parent / 'extract_pkg_from_dmg.py'
            
            if not extractor_script.exists():
                print(f"    ⚠️  Extractor script not found")
                return None
            
            result = subprocess.run(
                [sys.executable, str(extractor_script), str(dmg_path), str(dmg_path.parent)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Find the extracted PKG
                dmg_stem = dmg_path.stem
                possible_names = [
                    dmg_path.with_suffix('.pkg'),
                    dmg_path.parent / f"{dmg_stem}.pkg",
                    dmg_path.parent / "JamfConnect.pkg",  # Common specific names
                    dmg_path.parent / "Installer.pkg"
                ]
                
                for pkg_path in possible_names:
                    if pkg_path.exists():
                        print(f"    ✅ Extracted PKG: {pkg_path.name}")
                        return pkg_path
                
                print(f"    ⚠️  PKG file not found after extraction")
                return None
            else:
                print(f"    ⚠️  Extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"    ⚠️  Extraction error: {str(e)}")
            return None
    
    def convert_dmg_to_pkg(self, dmg_path):
        """Convert DMG to PKG for Jamf compatibility"""
        print(f"  🔄 Converting DMG to PKG for Jamf compatibility...")
        
        try:
            # Use the dmg_to_pkg.py script
            converter_script = Path(__file__).parent / 'dmg_to_pkg.py'
            
            if not converter_script.exists():
                print(f"    ⚠️  Converter script not found, skipping conversion")
                return None
            
            # Run the conversion
            result = subprocess.run(
                [sys.executable, str(converter_script), str(dmg_path), str(dmg_path.parent)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Find the created PKG file
                pkg_path = dmg_path.with_suffix('.pkg')
                if pkg_path.exists():
                    # Remove the original DMG to save space
                    dmg_path.unlink()
                    print(f"    ✅ Converted to PKG: {pkg_path.name}")
                    return pkg_path
                else:
                    print(f"    ⚠️  PKG file not found after conversion")
                    return None
            else:
                print(f"    ⚠️  Conversion failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"    ⚠️  Conversion error: {str(e)}")
            return None
        
    def verify_signature(self, filepath, team_id):
        """Verify package signature using Team ID"""
        verify_script = Path(__file__).parent / 'verify_signature.py'
        
        if not verify_script.exists():
            print(f"    ⚠️  Signature verification script not found")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(verify_script), str(filepath), team_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  🔐 {result.stdout.strip()}")
                return True
            else:
                print(f"  ❌ {result.stdout.strip()}")
                return False
                
        except Exception as e:
            print(f"    ⚠️  Signature verification error: {str(e)}")
            return False
    
    def calculate_hash(self, filepath):
        """Calculate SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def scan_virustotal(self, filepath, file_hash):
        """Scan file with VirusTotal API v3"""
        headers = {'x-apikey': self.vt_api_key}
        
        # First, check if file is already in VirusTotal by hash
        report_url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        response = requests.get(report_url, headers=headers)
        
        if response.status_code == 200:
            # File already scanned
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            
            return {
                'status': 'already_scanned',
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'harmless': stats.get('harmless', 0),
                'undetected': stats.get('undetected', 0),
                'scan_date': data['data']['attributes'].get('last_analysis_date', 'unknown')
            }
        
        elif response.status_code == 404:
            # File not scanned before, need to upload
            print(f"    Uploading to VirusTotal for analysis...")
            
            # Check file size to determine upload URL
            file_size = filepath.stat().st_size
            if file_size > 32 * 1024 * 1024:  # 32MB
                # Get special upload URL for large files
                upload_url_response = requests.get(
                    "https://www.virustotal.com/api/v3/files/upload_url",
                    headers=headers
                )
                if upload_url_response.status_code == 200:
                    upload_url = upload_url_response.json()['data']
                else:
                    print(f"    Warning: Could not get upload URL for large file")
                    return {'error': 'Could not get upload URL'}
            else:
                upload_url = "https://www.virustotal.com/api/v3/files"
            
            # Upload file
            with open(filepath, 'rb') as f:
                files = {'file': (filepath.name, f)}
                response = requests.post(upload_url, headers=headers, files=files)
            
            if response.status_code != 200:
                print(f"    Warning: Upload failed with status {response.status_code}")
                return {'error': f'Upload failed: {response.status_code}'}
            
            analysis_id = response.json()['data']['id']
            print(f"    Analysis started, waiting for results...")
            
            # Poll for results (max 5 minutes)
            max_attempts = 20
            for attempt in range(max_attempts):
                time.sleep(15)  # Wait 15 seconds between checks
                
                analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
                response = requests.get(analysis_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data['data']['attributes']['status']
                    
                    print(f"    Status: {status} (attempt {attempt + 1}/{max_attempts})")
                    
                    if status == 'completed':
                        stats = data['data']['attributes']['stats']
                        
                        return {
                            'status': 'new_scan',
                            'malicious': stats.get('malicious', 0),
                            'suspicious': stats.get('suspicious', 0),
                            'harmless': stats.get('harmless', 0),
                            'undetected': stats.get('undetected', 0),
                            'scan_date': datetime.now().isoformat()
                        }
            
            print(f"    Warning: Analysis timeout after {max_attempts * 15} seconds")
            return {'error': 'Analysis timeout'}
        
        else:
            print(f"    Warning: Unexpected VirusTotal response: {response.status_code}")
            return {'error': f'Unexpected response: {response.status_code}'}

if __name__ == '__main__':
    processor = MVPProcessor()
    processor.process_all()