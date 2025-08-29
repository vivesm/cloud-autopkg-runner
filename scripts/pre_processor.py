#!/usr/bin/env python3
"""
Pre-processor for AutoPkg runs
Validates environment and prepares for processing
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PreProcessor:
    """Pre-processing validation and setup"""
    
    def __init__(self):
        self.workspace = Path(os.environ.get('WORKSPACE', '/workspace'))
        self.errors = []
        self.warnings = []
        
    def validate_environment(self):
        """Validate required environment variables"""
        required_vars = {
            'JAMF_URL': 'Jamf Pro URL',
            'JAMF_USERNAME': 'Jamf Pro username',
            'JAMF_PASSWORD': 'Jamf Pro password',
            'VIRUSTOTAL_API_KEY': 'VirusTotal API key'
        }
        
        missing = []
        for var, description in required_vars.items():
            if not os.environ.get(var):
                missing.append(f"{var} ({description})")
                
        if missing:
            self.errors.append(f"Missing required environment variables: {', '.join(missing)}")
            return False
            
        logger.info("Environment validation successful")
        return True
        
    def validate_recipes(self):
        """Validate recipe files exist"""
        recipe_list = self.workspace / 'autopkg' / 'RecipeList.txt'
        
        if not recipe_list.exists():
            self.errors.append(f"Recipe list not found: {recipe_list}")
            return False
            
        with open(recipe_list) as f:
            recipes = [line.strip() for line in f if line.strip()]
            
        missing_recipes = []
        for recipe in recipes:
            recipe_file = self.workspace / 'autopkg' / 'overrides' / f"{recipe}.recipe.yaml"
            if not recipe_file.exists():
                missing_recipes.append(str(recipe_file))
                
        if missing_recipes:
            self.errors.append(f"Missing recipe files: {', '.join(missing_recipes)}")
            return False
            
        logger.info(f"Validated {len(recipes)} recipes")
        return True
        
    def test_jamf_connection(self):
        """Test Jamf Pro API connection"""
        import requests
        from requests.auth import HTTPBasicAuth
        
        jamf_url = os.environ.get('JAMF_URL')
        username = os.environ.get('JAMF_USERNAME')
        password = os.environ.get('JAMF_PASSWORD')
        
        try:
            response = requests.get(
                f"{jamf_url}/api/v1/auth/token",
                auth=HTTPBasicAuth(username, password),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Jamf Pro connection successful")
                return True
            else:
                self.errors.append(f"Jamf Pro authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.errors.append(f"Jamf Pro connection failed: {str(e)}")
            return False
            
    def test_virustotal_connection(self):
        """Test VirusTotal API connection"""
        import requests
        
        api_key = os.environ.get('VIRUSTOTAL_API_KEY')
        
        try:
            response = requests.get(
                "https://www.virustotal.com/api/v3/users/current",
                headers={'x-apikey': api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("VirusTotal connection successful")
                return True
            else:
                self.warnings.append(f"VirusTotal API test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.warnings.append(f"VirusTotal connection failed: {str(e)}")
            return False
            
    def prepare_directories(self):
        """Create required directories"""
        directories = [
            self.workspace / 'reports',
            self.workspace / 'cache',
            self.workspace / 'downloads',
            self.workspace / 'logs'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
            
    def generate_report(self):
        """Generate pre-processing report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success' if not self.errors else 'failed',
            'errors': self.errors,
            'warnings': self.warnings,
            'environment': {
                'workspace': str(self.workspace),
                'python_version': sys.version,
                'platform': sys.platform
            }
        }
        
        report_file = self.workspace / 'reports' / f"pre-process-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Pre-processing report saved: {report_file}")
        return report
        
    def run(self):
        """Run all pre-processing checks"""
        logger.info("Starting pre-processing validation")
        
        checks = [
            ('Environment Variables', self.validate_environment),
            ('Recipe Files', self.validate_recipes),
            ('Jamf Pro Connection', self.test_jamf_connection),
            ('VirusTotal API', self.test_virustotal_connection)
        ]
        
        for check_name, check_func in checks:
            logger.info(f"Running check: {check_name}")
            if not check_func():
                if check_name in ['Environment Variables', 'Recipe Files', 'Jamf Pro Connection']:
                    logger.error(f"Critical check failed: {check_name}")
                    break
                else:
                    logger.warning(f"Non-critical check failed: {check_name}")
                    
        self.prepare_directories()
        report = self.generate_report()
        
        if self.errors:
            logger.error("Pre-processing failed with errors")
            sys.exit(1)
        else:
            logger.info("Pre-processing completed successfully")
            return report


if __name__ == '__main__':
    processor = PreProcessor()
    processor.run()