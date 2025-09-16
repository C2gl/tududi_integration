#!/usr/bin/env python3
"""
Validate that all translation files have equivalent keys to the base strings.json file.
"""

import json
import os
import sys
from pathlib import Path

def get_all_keys(obj, prefix=''):
    """Recursively get all keys from a nested dictionary."""
    keys = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_key = f"{prefix}.{key}" if prefix else key
            keys.add(current_key)
            if isinstance(value, dict):
                keys.update(get_all_keys(value, current_key))
    return keys

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        # Check if file is empty first
        if file_path.stat().st_size == 0:
            print(f"⚠️  Empty file: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print(f"⚠️  Empty content: {file_path}")
                return None
            return json.loads(content)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        return None

def main():
    # Base strings file
    base_strings_path = Path("custom_components/tududi_integration/strings.json")
    translations_dir = Path("custom_components/tududi_integration/translations")

    if not base_strings_path.exists():
        print(f"❌ Base strings file not found: {base_strings_path}")
        sys.exit(1)
    
    # Load base strings
    base_data = load_json_file(base_strings_path)
    if base_data is None:
        sys.exit(1)
    
    base_keys = get_all_keys(base_data)
    print(f"📋 Base strings.json has {len(base_keys)} keys")
    
    # Check if translations directory exists
    if not translations_dir.exists():
        print(f"ℹ️  No translations directory found at {translations_dir}")
        print("✅ No translation files to validate")
        return
    
    # Find all translation files
    translation_files = list(translations_dir.glob("*.json"))
    
    if not translation_files:
        print("ℹ️  No translation files found")
        print("✅ No translation files to validate")
        return
    
    print(f"🔍 Found {len(translation_files)} translation files")
    
    errors = []
    
    for trans_file in translation_files:
        file_name = trans_file.stem  # Just the filename without .json extension
        print(f"\n📄 Checking {file_name}.json...")
        
        trans_data = load_json_file(trans_file)
        if trans_data is None:
            print(f"  ⚠️  Skipping {file_name}.json - file is empty or invalid")
            continue  # Skip this file, don't count as error
        
        trans_keys = get_all_keys(trans_data)
        
        # Check for missing keys
        missing_keys = base_keys - trans_keys
        extra_keys = trans_keys - base_keys
        
        if missing_keys:
            print(f"  ❌ Missing {len(missing_keys)} keys:")
            for key in sorted(missing_keys):
                print(f"    - {key}")
            errors.append(f"{file_name}.json: missing {len(missing_keys)} keys")
        
        if extra_keys:
            print(f"  ⚠️  Extra {len(extra_keys)} keys (not in base):")
            for key in sorted(extra_keys):
                print(f"    + {key}")
        
        if not missing_keys and not extra_keys:
            print(f"  ✅ All keys match ({len(trans_keys)} keys)")
    
    if errors:
        print(f"\n❌ Translation validation found issues:")
        for error in errors:
            print(f"  - {error}")
        print(f"\n💡 Consider updating translation files.")
        sys.exit(1)
    else:
        print(f"\n✅ All translation files are complete!")

if __name__ == "__main__":
    main()
