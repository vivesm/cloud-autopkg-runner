#!/usr/bin/env python3
"""
Generate HTML report from AutoPkg run results
"""

import json
import os
from pathlib import Path
from datetime import datetime

class HTMLReportGenerator:
    def __init__(self):
        self.reports_dir = Path(__file__).parent.parent / 'reports'
        self.results_file = self.reports_dir / 'results.json'
        
    def generate(self):
        """Generate HTML report from JSON results"""
        if not self.results_file.exists():
            print("No results.json file found")
            return
            
        with open(self.results_file) as f:
            data = json.load(f)
        
        # Calculate statistics
        apps = data.get('apps', [])
        success_count = sum(1 for app in apps if app.get('status') == 'success')
        failed_count = sum(1 for app in apps if app.get('status') == 'failed')
        total_count = len(apps)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoPkg Run Report - {data.get('timestamp', 'Unknown')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .timestamp {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            margin-top: 0.5rem;
        }}
        
        .success {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        
        .content {{
            padding: 2rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 2rem;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }}
        
        td {{
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 2rem 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        
        .error-details {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 1rem;
            margin-top: 0.5rem;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9rem;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 2rem;
            text-align: center;
            color: #666;
        }}
        
        .vt-stats {{
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
        }}
        
        .vt-stat {{
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 AutoPkg Run Report</h1>
            <div class="timestamp">📅 {data.get('timestamp', 'Unknown')}</div>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total_count}</div>
                <div class="stat-label">Total Apps</div>
            </div>
            <div class="stat-card">
                <div class="stat-value success">{success_count}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-card">
                <div class="stat-value failed">{failed_count}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{success_rate:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>
        
        <div class="content">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {success_rate}%">
                    {success_rate:.1f}% Complete
                </div>
            </div>
            
            <h2>📦 Application Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Application</th>
                        <th>Status</th>
                        <th>Size</th>
                        <th>VirusTotal</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add table rows for each app
        for app in apps:
            status = app.get('status', 'unknown')
            status_badge = 'badge-success' if status == 'success' else 'badge-danger'
            status_icon = '✅' if status == 'success' else '❌'
            
            # VirusTotal results
            vt_html = ''
            if 'virustotal' in app:
                vt = app['virustotal']
                if vt.get('skipped'):
                    vt_html = '<span class="badge badge-warning">Skipped</span>'
                elif vt.get('error'):
                    vt_html = f'<span class="badge badge-danger">Error</span>'
                else:
                    malicious = vt.get('malicious', 0)
                    harmless = vt.get('harmless', 0)
                    badge_class = 'badge-success' if malicious == 0 else 'badge-danger' if malicious > 5 else 'badge-warning'
                    vt_html = f'''
                        <span class="badge {badge_class}">{malicious} threats</span>
                        <div class="vt-stats">
                            <span class="vt-stat">✅ {harmless} clean</span>
                            <span class="vt-stat">⚠️ {vt.get('suspicious', 0)} suspicious</span>
                        </div>
                    '''
            else:
                vt_html = '<span class="badge badge-info">Not scanned</span>'
            
            # Details column
            details_html = ''
            if status == 'success':
                if 'path' in app:
                    details_html = f"✅ Downloaded successfully"
                if 'hash_verification' in app:
                    details_html += f"<br>🔐 Hash verified"
            else:
                if 'error' in app:
                    details_html = f'<div class="error-details">{app["error"]}</div>'
            
            # Size
            size_html = f"{app.get('size_mb', 'N/A')} MB" if 'size_mb' in app else 'N/A'
            
            html += f"""
                    <tr>
                        <td><strong>{app.get('name', 'Unknown')}</strong></td>
                        <td><span class="badge {status_badge}">{status_icon} {status}</span></td>
                        <td>{size_html}</td>
                        <td>{vt_html}</td>
                        <td>{details_html}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <footer>
            <p><strong>AutoPkg MVP Runner</strong></p>
            <p>Generated by GitHub Actions • Run #{run_number}</p>
            <p>View on <a href="{repo_url}">GitHub</a></p>
        </footer>
    </div>
</body>
</html>
"""
        
        # Replace placeholders
        html = html.replace('{run_number}', os.environ.get('GITHUB_RUN_NUMBER', 'Unknown'))
        html = html.replace('{repo_url}', f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}")
        
        # Save HTML report
        output_file = self.reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w') as f:
            f.write(html)
        
        # Also save as latest
        latest_file = self.reports_dir / 'report.html'
        with open(latest_file, 'w') as f:
            f.write(html)
        
        print(f"HTML report generated: {output_file}")
        print(f"Latest report: {latest_file}")

if __name__ == '__main__':
    generator = HTMLReportGenerator()
    generator.generate()