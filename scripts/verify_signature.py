#!/usr/bin/env python3
"""
Code Signature Verification Script
Verifies package signatures using Apple Developer Team IDs
"""

import subprocess
import re
import sys
from pathlib import Path

def verify_package_signature(package_path, expected_team_id):
    """
    Verify package signature using spctl and pkgutil
    Returns: (success, message)
    """
    package_path = Path(package_path)
    
    if not package_path.exists():
        return False, f"Package not found: {package_path}"
    
    # Check if it's a PKG file
    if package_path.suffix.lower() == '.pkg':
        return verify_pkg_signature(package_path, expected_team_id)
    elif package_path.suffix.lower() == '.dmg':
        return verify_dmg_signature(package_path, expected_team_id)
    else:
        return False, f"Unsupported file type: {package_path.suffix}"

def verify_pkg_signature(pkg_path, expected_team_id):
    """Verify PKG file signature"""
    try:
        # Use pkgutil to check signature
        result = subprocess.run(
            ['pkgutil', '--check-signature', str(pkg_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False, "Package is not signed"
        
        # Extract team ID from output
        # Look for pattern like "Developer ID Installer: Company Name (TEAMID)"
        team_id_pattern = r'Developer ID .*?\(([A-Z0-9]{10})\)'
        matches = re.findall(team_id_pattern, result.stdout)
        
        if not matches:
            # Try alternate pattern for certificates
            team_id_pattern = r'Certificate.*?\(([A-Z0-9]{10})\)'
            matches = re.findall(team_id_pattern, result.stdout)
        
        if not matches:
            return False, "Could not extract Team ID from signature"
        
        found_team_id = matches[0]
        
        if found_team_id == expected_team_id:
            return True, f"Signature verified: Team ID {found_team_id} matches"
        else:
            return False, f"Team ID mismatch: expected {expected_team_id}, found {found_team_id}"
            
    except subprocess.CalledProcessError as e:
        return False, f"Error checking signature: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def verify_dmg_signature(dmg_path, expected_team_id):
    """Verify DMG file signature"""
    try:
        # Use spctl to assess the DMG
        result = subprocess.run(
            ['spctl', '-a', '-vvv', '-t', 'open', '--context', 'context:primary-signature', str(dmg_path)],
            capture_output=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        
        # spctl returns 0 for valid signature
        if result.returncode != 0:
            return False, "DMG signature verification failed"
        
        # Extract team ID from output
        # Look for pattern like "origin=Developer ID Application: Company (TEAMID)"
        team_id_pattern = r'origin=.*?\(([A-Z0-9]{10})\)'
        matches = re.findall(team_id_pattern, result.stdout)
        
        if not matches:
            return False, "Could not extract Team ID from DMG signature"
        
        found_team_id = matches[0]
        
        if found_team_id == expected_team_id:
            return True, f"DMG signature verified: Team ID {found_team_id} matches"
        else:
            return False, f"Team ID mismatch: expected {expected_team_id}, found {found_team_id}"
            
    except subprocess.CalledProcessError as e:
        return False, f"Error checking DMG signature: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def extract_team_id(package_path):
    """
    Extract the Team ID from a package without verification
    Useful for discovering the Team ID of a package
    """
    package_path = Path(package_path)
    
    if package_path.suffix.lower() == '.pkg':
        result = subprocess.run(
            ['pkgutil', '--check-signature', str(package_path)],
            capture_output=True,
            text=True
        )
        
        # Extract all team IDs found
        team_id_pattern = r'\(([A-Z0-9]{10})\)'
        matches = re.findall(team_id_pattern, result.stdout)
        
        if matches:
            return matches[0], result.stdout
        else:
            return None, result.stdout
            
    elif package_path.suffix.lower() == '.dmg':
        result = subprocess.run(
            ['spctl', '-a', '-vvv', '-t', 'open', '--context', 'context:primary-signature', str(package_path)],
            capture_output=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        
        team_id_pattern = r'origin=.*?\(([A-Z0-9]{10})\)'
        matches = re.findall(team_id_pattern, result.stdout)
        
        if matches:
            return matches[0], result.stdout
        else:
            return None, result.stdout
    
    return None, "Unsupported file type"

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Verify:   python3 verify_signature.py <package_file> <expected_team_id>")
        print("  Extract:  python3 verify_signature.py <package_file>")
        sys.exit(1)
    
    package_file = sys.argv[1]
    
    if len(sys.argv) == 2:
        # Extract mode
        team_id, output = extract_team_id(package_file)
        if team_id:
            print(f"✅ Found Team ID: {team_id}")
            print("\nFull signature info:")
            print(output)
        else:
            print(f"❌ Could not extract Team ID")
            print("\nOutput:")
            print(output)
    else:
        # Verify mode
        expected_team_id = sys.argv[2]
        success, message = verify_package_signature(package_file, expected_team_id)
        
        if success:
            print(f"✅ {message}")
            sys.exit(0)
        else:
            print(f"❌ {message}")
            sys.exit(1)

if __name__ == '__main__':
    main()