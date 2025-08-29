#!/usr/bin/env python3
"""
Extract PKG from DMG
For apps like Jamf Connect that distribute PKG inside DMG
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def extract_pkg_from_dmg(dmg_path, output_dir=None):
    """Extract PKG file from DMG"""
    mount_point = None
    
    try:
        dmg_path = Path(dmg_path)
        if output_dir is None:
            output_dir = dmg_path.parent
        
        print(f"  📀 Mounting DMG: {dmg_path.name}")
        
        # Mount the DMG (using yes to auto-accept license agreements)
        mount_cmd = f"yes | hdiutil attach '{str(dmg_path)}' -nobrowse -noverify -noautoopen"
        result = subprocess.run(
            mount_cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to mount DMG: {result.stderr}")
        
        # Parse mount output to find mount point
        for line in result.stdout.split('\n'):
            if '/Volumes/' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    mount_point = parts[-1].strip()
                    break
        
        if not mount_point:
            raise Exception("Could not determine mount point")
        
        print(f"  ✅ Mounted at: {mount_point}")
        
        # Find PKG files
        pkgs = []
        for item in os.listdir(mount_point):
            if item.endswith('.pkg') and not item.startswith('.'):
                pkg_path = os.path.join(mount_point, item)
                if os.path.isfile(pkg_path):
                    pkgs.append(pkg_path)
        
        if not pkgs:
            raise Exception("No PKG file found in DMG")
        
        if len(pkgs) > 1:
            print(f"  ⚠️  Multiple PKGs found, using first: {Path(pkgs[0]).name}")
        
        # Copy PKG to output directory
        source_pkg = pkgs[0]
        pkg_name = Path(source_pkg).name
        
        # Use the DMG name for the PKG if it's a generic name
        if pkg_name.lower() in ['installer.pkg', 'install.pkg', 'package.pkg']:
            pkg_name = dmg_path.stem + '.pkg'
        
        dest_pkg = Path(output_dir) / pkg_name
        
        print(f"  📦 Extracting: {pkg_name}")
        shutil.copy2(source_pkg, dest_pkg)
        
        # Unmount DMG
        print(f"  🔧 Unmounting DMG...")
        subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'], 
                      capture_output=True)
        
        # Remove original DMG to save space
        dmg_path.unlink()
        print(f"  ✅ Extracted PKG: {dest_pkg.name}")
        
        return str(dest_pkg)
        
    except Exception as e:
        # Cleanup on error
        if mount_point and os.path.exists(mount_point):
            subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'], 
                         capture_output=True)
        raise e

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python3 extract_pkg_from_dmg.py <dmg_file> [output_dir]")
        sys.exit(1)
    
    dmg_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        pkg_path = extract_pkg_from_dmg(dmg_file, output_dir)
        print(f"Success! PKG extracted to: {pkg_path}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()