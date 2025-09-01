#!/usr/bin/env python3
"""
Roo Framework Compatibility Validation Script
Validates that the memory-bank output is compatible with roo-autonomous-development-framework
"""

import json
import pathlib
import re
import sys
from typing import Dict, List, Optional

def validate_frontmatter(content: str, filename: str) -> List[str]:
    """Validate YAML frontmatter in markdown files"""
    errors = []
    
    # Check for frontmatter presence
    if not content.startswith('---\n'):
        errors.append(f"{filename}: Missing YAML frontmatter")
        return errors
    
    # Extract frontmatter
    try:
        end_idx = content.find('\n---\n', 4)
        if end_idx == -1:
            errors.append(f"{filename}: Malformed frontmatter (missing end marker)")
            return errors
        
        frontmatter = content[4:end_idx]
        
        # Check required fields
        required_fields = ['version', 'updated', 'title']
        for field in required_fields:
            if f'{field}:' not in frontmatter:
                errors.append(f"{filename}: Missing required frontmatter field: {field}")
        
        # Validate ISO timestamp format
        if 'updated:' in frontmatter:
            timestamp_match = re.search(r'updated:\s*(.+)', frontmatter)
            if timestamp_match:
                timestamp = timestamp_match.group(1).strip()
                # Basic ISO format check
                if not re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', timestamp):
                    errors.append(f"{filename}: Invalid timestamp format: {timestamp}")
    
    except Exception as e:
        errors.append(f"{filename}: Error parsing frontmatter: {e}")
    
    return errors

def validate_memory_bank_structure(memory_bank_dir: pathlib.Path) -> Dict[str, List[str]]:
    """Validate the memory-bank directory structure and content"""
    validation_results = {
        "structure": [],
        "content": [],
        "schemas": []
    }
    
    # Check required files
    required_files = [
        'productContext.md',
        'systemPatterns.md', 
        'decisionLog.md',
        'delegationPatterns.md',
        'learningHistory.md',
        'actionable-patterns.md',
        'global-patterns.md',
        'progress.md'
    ]
    
    # Validate directory structure
    if not memory_bank_dir.exists():
        validation_results["structure"].append("memory-bank directory does not exist")
        return validation_results
    
    if not memory_bank_dir.is_dir():
        validation_results["structure"].append("memory-bank is not a directory")
        return validation_results
    
    # Check required files
    for filename in required_files:
        file_path = memory_bank_dir / filename
        if not file_path.exists():
            validation_results["structure"].append(f"Missing required file: {filename}")
        elif not file_path.is_file():
            validation_results["structure"].append(f"Not a file: {filename}")
        else:
            # Validate file content
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Validate frontmatter
                frontmatter_errors = validate_frontmatter(content, filename)
                validation_results["content"].extend(frontmatter_errors)
                
                # Check minimum content length
                if len(content) < 200:
                    validation_results["content"].append(f"{filename}: Content too short (< 200 chars)")
                
                # File-specific validations
                if filename == 'actionable-patterns.md':
                    if 'PATTERN_' not in content:
                        validation_results["content"].append(f"{filename}: Missing pattern definitions")
                
                if filename == 'delegationPatterns.md':
                    if 'Success Rate' not in content:
                        validation_results["content"].append(f"{filename}: Missing success rate metrics")
                
            except Exception as e:
                validation_results["content"].append(f"{filename}: Error reading file: {e}")
    
    # Check schemas directory
    schemas_dir = memory_bank_dir / 'schemas'
    if not schemas_dir.exists():
        validation_results["schemas"].append("schemas directory missing")
    else:
        expected_schemas = [
            'programming-issues-pattern.json',
            'programming-issue-context.json'
        ]
        
        for schema_file in expected_schemas:
            schema_path = schemas_dir / schema_file
            if not schema_path.exists():
                validation_results["schemas"].append(f"Missing schema: {schema_file}")
            else:
                try:
                    with open(schema_path) as f:
                        schema_data = json.load(f)
                    
                    # Basic JSON schema validation
                    if '$schema' not in schema_data:
                        validation_results["schemas"].append(f"{schema_file}: Missing $schema field")
                    
                    if 'type' not in schema_data:
                        validation_results["schemas"].append(f"{schema_file}: Missing type field")
                        
                except json.JSONDecodeError as e:
                    validation_results["schemas"].append(f"{schema_file}: Invalid JSON: {e}")
                except Exception as e:
                    validation_results["schemas"].append(f"{schema_file}: Error reading schema: {e}")
    
    return validation_results

def validate_integration_files(base_dir: pathlib.Path) -> List[str]:
    """Validate integration-specific files"""
    errors = []
    
    # Check for integration metadata
    metadata_file = base_dir / 'memory-bank' / 'roo-integration-metadata.json'
    if not metadata_file.exists():
        errors.append("Missing roo-integration-metadata.json")
    else:
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            required_sections = ['integration_info', 'agent_access_methods', 'refresh_instructions']
            for section in required_sections:
                if section not in metadata:
                    errors.append(f"roo-integration-metadata.json: Missing section: {section}")
        
        except Exception as e:
            errors.append(f"roo-integration-metadata.json: Error reading metadata: {e}")
    
    return errors

def main():
    """Run compatibility validation"""
    print("🔍 Validating Roo Framework Compatibility...")
    
    base_dir = pathlib.Path('.')
    memory_bank_dir = base_dir / 'memory-bank'
    
    # Validate structure and content
    results = validate_memory_bank_structure(memory_bank_dir)
    integration_errors = validate_integration_files(base_dir)
    
    # Print results
    total_errors = 0
    
    for category, errors in results.items():
        if errors:
            print(f"\n❌ {category.title()} Issues:")
            for error in errors:
                print(f"   • {error}")
                total_errors += 1
        else:
            print(f"✅ {category.title()}: All checks passed")
    
    if integration_errors:
        print(f"\n❌ Integration Issues:")
        for error in integration_errors:
            print(f"   • {error}")
            total_errors += len(integration_errors)
    else:
        print("✅ Integration: All checks passed")
    
    # Summary
    if total_errors == 0:
        print(f"\n🎉 All compatibility checks passed!")
        print("✅ Memory bank is ready for Roo Framework integration")
        return 0
    else:
        print(f"\n⚠️  Found {total_errors} compatibility issues")
        print("❌ Please fix these issues before integrating with Roo Framework")
        return 1

if __name__ == '__main__':
    sys.exit(main())
