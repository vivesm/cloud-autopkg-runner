#!/usr/bin/env python3
"""
DMG to PKG Converter
Converts DMG disk images to PKG installers for Jamf Pro compatibility
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import plistlib
import json

class DMGtoPKGConverter:
    def __init__(self):
        self.temp_dir = None
        self.mount_point = None
        
    def cleanup(self):
        """Clean up temporary files and unmount DMG"""
        if self.mount_point and os.path.exists(self.mount_point):
            print(f"  🔧 Unmounting DMG...")
            subprocess.run(['hdiutil', 'detach', self.mount_point, '-quiet'], 
                         capture_output=True)
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def mount_dmg(self, dmg_path):
        """Mount DMG and return mount point"""
        print(f"  📀 Mounting DMG: {Path(dmg_path).name}")
        
        # Mount the DMG
        result = subprocess.run(
            ['hdiutil', 'attach', dmg_path, '-nobrowse', '-noverify', '-noautoopen'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to mount DMG: {result.stderr}")
        
        # Parse mount output to find mount point
        for line in result.stdout.split('\n'):
            if '/Volumes/' in line:
                # Extract mount point from output
                parts = line.split('\t')
                if len(parts) >= 3:
                    self.mount_point = parts[-1].strip()
                    print(f"  ✅ Mounted at: {self.mount_point}")
                    return self.mount_point
        
        raise Exception("Could not determine mount point")
    
    def find_app_bundle(self, mount_point):
        """Find the .app bundle in the mounted DMG"""
        print(f"  🔍 Looking for app bundle...")
        
        # Look for .app bundles
        apps = []
        for item in os.listdir(mount_point):
            if item.endswith('.app') and not item.startswith('.'):
                app_path = os.path.join(mount_point, item)
                if os.path.isdir(app_path):
                    apps.append(app_path)
        
        if not apps:
            raise Exception("No .app bundle found in DMG")
        
        if len(apps) > 1:
            print(f"  ⚠️  Multiple apps found, using first: {Path(apps[0]).name}")
        
        app_path = apps[0]
        print(f"  ✅ Found app: {Path(app_path).name}")
        return app_path
    
    def get_app_info(self, app_path):
        """Extract app information from Info.plist"""
        info_plist = os.path.join(app_path, 'Contents', 'Info.plist')
        
        if not os.path.exists(info_plist):
            raise Exception(f"Info.plist not found at {info_plist}")
        
        with open(info_plist, 'rb') as f:
            info = plistlib.load(f)
        
        app_info = {
            'name': info.get('CFBundleName', Path(app_path).stem),
            'identifier': info.get('CFBundleIdentifier', 'com.unknown.app'),
            'version': info.get('CFBundleShortVersionString', '1.0'),
            'bundle_version': info.get('CFBundleVersion', '1'),
        }
        
        print(f"  📋 App info: {app_info['name']} v{app_info['version']} ({app_info['identifier']})")
        return app_info
    
    def create_pkg(self, app_path, app_info, output_path):
        """Create PKG installer from app bundle"""
        print(f"  📦 Creating PKG installer...")
        
        # Create temporary directory for package building
        self.temp_dir = tempfile.mkdtemp(prefix='dmg2pkg_')
        
        # Create payload directory structure
        payload_dir = os.path.join(self.temp_dir, 'payload')
        apps_dir = os.path.join(payload_dir, 'Applications')
        os.makedirs(apps_dir)
        
        # Copy app to payload
        app_name = Path(app_path).name
        dest_app = os.path.join(apps_dir, app_name)
        print(f"  📁 Copying {app_name} to staging...")
        shutil.copytree(app_path, dest_app, symlinks=True)
        
        # Build the package
        pkg_args = [
            'pkgbuild',
            '--root', payload_dir,
            '--identifier', app_info['identifier'],
            '--version', app_info['version'],
            '--install-location', '/',
            output_path
        ]
        
        print(f"  🔨 Building package...")
        result = subprocess.run(pkg_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"pkgbuild failed: {result.stderr}")
        
        # Verify package was created
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / 1024 / 1024
            print(f"  ✅ PKG created: {Path(output_path).name} ({size_mb:.2f} MB)")
            return True
        else:
            raise Exception("PKG file was not created")
    
    def convert(self, dmg_path, output_dir=None):
        """Main conversion function"""
        try:
            # Validate input
            if not os.path.exists(dmg_path):
                raise Exception(f"DMG file not found: {dmg_path}")
            
            if not dmg_path.lower().endswith('.dmg'):
                raise Exception(f"Not a DMG file: {dmg_path}")
            
            # Determine output path
            if output_dir is None:
                output_dir = Path(dmg_path).parent
            
            dmg_name = Path(dmg_path).stem
            output_path = os.path.join(output_dir, f"{dmg_name}.pkg")
            
            print(f"\n🔄 Converting DMG to PKG: {Path(dmg_path).name}")
            print(f"  Source: {dmg_path}")
            print(f"  Target: {output_path}")
            
            # Mount DMG
            mount_point = self.mount_dmg(dmg_path)
            
            # Find app bundle
            app_path = self.find_app_bundle(mount_point)
            
            # Get app information
            app_info = self.get_app_info(app_path)
            
            # Create PKG
            self.create_pkg(app_path, app_info, output_path)
            
            print(f"\n✅ Conversion complete: {Path(output_path).name}")
            return output_path
            
        except Exception as e:
            print(f"\n❌ Conversion failed: {str(e)}")
            return None
            
        finally:
            self.cleanup()


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python3 dmg_to_pkg.py <dmg_file> [output_dir]")
        sys.exit(1)
    
    dmg_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    converter = DMGtoPKGConverter()
    result = converter.convert(dmg_file, output_dir)
    
    if result:
        print(f"Success! PKG saved to: {result}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()