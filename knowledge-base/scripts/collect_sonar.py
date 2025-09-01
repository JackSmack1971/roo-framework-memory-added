#!/usr/bin/env python3
"""
Enhanced SonarCloud Issue Collection Script
Uses SonarCloud v2 API with Bearer token authentication
"""

import argparse
import json
import time
import requests
import hashlib
from pathlib import Path
from urllib.parse import urljoin
from typing import Dict, List, Optional

# Import local utilities
try:
    from json_utils import load_json
    from emit_issue import write_issues_batch
except ImportError:
    print("Warning: Could not import local utilities. Some functions may not work.")

def get_api_headers(token: str) -> Dict[str, str]:
    """Generate headers for SonarCloud API v2 with Bearer authentication"""
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'User-Agent': 'roo-framework-knowledge-base/1.0'
    }

def fetch_rules_page(base_url: str, token: str, languages: List[str], 
                    page: int = 1, page_size: int = 100) -> Optional[Dict]:
    """
    Fetch a page of rules from SonarCloud v2 API
    """
    # Use the new v2 API endpoint
    api_url = "https://api.sonarcloud.io"
    
    params = {
        'languages': ','.join(languages),
        'p': page,
        'ps': page_size,
        'types': 'CODE_SMELL,BUG,VULNERABILITY,SECURITY_HOTSPOT',
        'activation': 'true',
        'qprofile': None,  # Get rules for all quality profiles
        'repositories': None,  # Get rules from all repositories
        'include_external': 'false',
        'statuses': 'READY'
    }
    
    # Clean up None values
    params = {k: v for k, v in params.items() if v is not None}
    
    headers = get_api_headers(token)
    
    try:
        # Try v2 API first
        v2_url = f"{api_url}/v2/clean-code-policy/rules/search"
        
        print(f"[SEARCH] Fetching rules from {v2_url} (page {page})")
        response = requests.get(v2_url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 404:
            # Fall back to v1 API if v2 is not available
            print("[CONFIG] v2 API not available, falling back to v1...")
            v1_url = f"{base_url}/api/rules/search"
            response = requests.get(v1_url, headers=headers, params=params, timeout=30)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response content: {e.response.text[:500]}...")
        return None

def extract_issue_data(rule: Dict, base_url: str) -> Dict:
    """
    Extract and normalize issue data from SonarCloud rule
    """
    key = rule.get('key', '')
    title = rule.get('name', '')
    desc = rule.get('htmlDesc', rule.get('description', ''))
    
    # Remove HTML tags from description for cleaner text
    import re
    if desc:
        desc = re.sub(r'<[^>]+>', '', desc)
        desc = desc.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    
    # Extract metadata
    severity = rule.get('severity', 'UNKNOWN').lower()
    rule_type = rule.get('type', 'UNKNOWN').lower()
    language = rule.get('lang', 'unknown').lower()
    
    # Extract taxonomy information
    cwe = []
    owasp = []
    sans_top25 = []
    
    if 'securityStandards' in rule:
        standards = rule['securityStandards']
        cwe = standards.get('cwe', [])
        owasp = standards.get('owaspTop10', [])
        sans_top25 = standards.get('sansTop25', [])
    
    # Generate consistent issue ID
    issue_id = hashlib.sha1(f'sonar|{key}'.encode()).hexdigest()
    
    # Build the issue document
    doc = {
        'issue_id': issue_id,
        'source': 'sonar',
        'source_rule_id': key,
        'language': language,
        'title': title[:240] if title else 'Untitled Issue',
        'summary': desc[:1000] if desc else None,
        'root_cause': None,  # Will be enhanced later with AI analysis
        'fix_steps': None,   # Will be enhanced later with AI analysis  
        'autofix_snippet': None,  # Will be enhanced later with AI analysis
        'severity': severity,
        'confidence': None,
        'taxonomy': {
            'cwe': cwe,
            'owasp': owasp,
            'sans_top25': sans_top25
        },
        'frequency': None,
        'signals': [{'kind': 'rule_id', 'value': key}],
        'references': [
            {
                'label': 'SonarCloud Rule Details',
                'url': f"{base_url}/organizations/sonarcloud/rules?rule_key={key}",
                'license': 'SonarCloud Community'
            }
        ],
        'metadata': {
            'type': rule_type,
            'tags': rule.get('sysTags', []),
            'remediation': rule.get('remediationFunction'),
            'effort': rule.get('defaultRemFnBaseEffort'),
            'created': rule.get('createdAt'),
            'repository': rule.get('repo', 'unknown')
        }
    }
    
    return doc

def collect_sonar_issues(base_url: str, token: str, languages: List[str], 
                        limit: Optional[int] = None, page_size: int = 100) -> int:
    """
    Main collection function for SonarCloud issues
    """
    print(f"[*] Starting SonarCloud issue collection...")
    print(f"[BASE] Base URL: {base_url}")  
    print(f"[LANGS] Languages: {', '.join(languages)}")
    print(f"[STATS] Limit: {limit or 'unlimited'}")
    
    total_collected = 0
    page = 1
    batch = []
    
    while True:
        # Fetch page of rules
        data = fetch_rules_page(base_url, token, languages, page, page_size)
        
        if not data:
            print(f"[ERROR] Failed to fetch page {page}")
            break
        
        rules = data.get('rules', [])
        if not rules:
            print(f"[PAGE] No more rules on page {page}")
            break
        
        print(f"[CONFIG] Processing {len(rules)} rules from page {page}")
        
        # Process each rule
        for rule in rules:
            try:
                doc = extract_issue_data(rule, base_url)
                batch.append(doc)
                total_collected += 1
                
                # Write batch if it's full
                if len(batch) >= 50:  # Write in smaller batches
                    write_issues_batch(batch)
                    batch = []
                    print(f"[SAVE] Wrote batch, total collected: {total_collected}")
                
                # Check limit
                if limit and total_collected >= limit:
                    print(f"[TARGET] Reached collection limit of {limit}")
                    break
                    
            except Exception as e:
                print(f"[WARNING]  Error processing rule {rule.get('key', 'unknown')}: {e}")
                continue
        
        # Write final batch for this page
        if batch:
            write_issues_batch(batch)
            batch = []
        
        # Check if we should continue
        if limit and total_collected >= limit:
            break
        
        # Check if there are more pages
        total_rules = data.get('total', 0)
        if page * page_size >= total_rules:
            print(f"[PAGE] Processed all {total_rules} available rules")
            break
        
        page += 1
        
        # Rate limiting - be respectful to SonarCloud API
        time.sleep(0.2)
    
    # Write any remaining batch
    if batch:
        write_issues_batch(batch)
    
    print(f"[OK] Collection completed! Collected {total_collected} issues")
    return total_collected

def validate_token(token: str, base_url: str = "https://sonarcloud.io") -> bool:
    """
    Validate that the API token works
    """
    headers = get_api_headers(token)
    
    # Test with a simple API call
    test_url = f"{base_url}/api/system/status"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        response.raise_for_status()
        print("[OK] API token validation successful")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API token validation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Collect programming issues from SonarCloud using v2 API"
    )
    parser.add_argument(
        '--base', 
        default='https://sonarcloud.io',
        help='SonarCloud base URL (default: https://sonarcloud.io)'
    )
    parser.add_argument(
        '--token',
        help='SonarCloud API token (or set SONAR_TOKEN environment variable)'
    )
    parser.add_argument(
        '--langs', 
        default='py,js,java',
        help='Programming languages (comma-separated, default: py,js,java)'
    )
    parser.add_argument(
        '--limit', 
        type=int,
        help='Maximum number of issues to collect'
    )
    parser.add_argument(
        '--page-size',
        type=int,
        default=100,
        help='Number of rules per API request (default: 100)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate API token, do not collect issues'
    )
    
    args = parser.parse_args()
    
    # Get API token
    token = args.token
    if not token:
        import os
        token = os.getenv('SONAR_TOKEN')
    
    if not token:
        print("[ERROR] Error: SonarCloud API token required")
        print("Provide via --token argument or SONAR_TOKEN environment variable")
        return 1
    
    # Validate token first
    if not validate_token(token, args.base):
        return 1
    
    if args.validate_only:
        print("[OK] Token validation successful - ready for collection")
        return 0
    
    # Parse languages
    languages = [lang.strip() for lang in args.langs.split(',')]
    
    try:
        # Run collection
        total = collect_sonar_issues(
            base_url=args.base,
            token=token,
            languages=languages,
            limit=args.limit,
            page_size=args.page_size
        )
        
        print(f"\n[SUCCESS] Successfully collected {total} issues")
        print("[FOLDER] Issues saved to: issuesdb/issues/")
        print("[RUNNING] Next step: Run 'python scripts/build_index.py' to build search index")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[WARNING]  Collection interrupted by user")
        return 130
    except Exception as e:
        print(f"\n[ERROR] Collection failed: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
