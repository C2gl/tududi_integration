"""
Installation verification script for Tududi HACS integration.

This script helps verify that the integration files are properly installed
and can be imported without errors.
"""

import sys
import os
from pathlib import Path

def verify_installation():
    """Verify that all required files are present and valid."""
    
    print("🔍 Verifying Tududi HACS installation...")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "custom_components" / "tududi_hacs").exists():
        print("❌ Error: This script must be run from the Home Assistant config directory")
        print("   Expected to find: custom_components/tududi_hacs/")
        return False
    
    integration_dir = current_dir / "custom_components" / "tududi_hacs"
    
    # Check required files
    required_files = [
        "__init__.py",
        "manifest.json", 
        "config_flow.py",
        "const.py",
        "sensor.py",
        "strings.json"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = integration_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Installation incomplete. Missing files: {missing_files}")
        return False
    
    # Test syntax of Python files
    print("\n🔍 Checking Python syntax...")
    python_files = ["__init__.py", "config_flow.py", "const.py", "sensor.py"]
    
    for py_file in python_files:
        try:
            file_path = integration_dir / py_file
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
            print(f"✅ {py_file} - Syntax OK")
        except SyntaxError as e:
            print(f"❌ {py_file} - Syntax Error: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {py_file} - Warning: {e}")
    
    # Check manifest.json
    print("\n🔍 Checking manifest.json...")
    try:
        import json
        with open(integration_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_keys = ["domain", "name", "version", "requirements"]
        for key in required_keys:
            if key in manifest:
                print(f"✅ manifest.{key}: {manifest[key]}")
            else:
                print(f"❌ manifest.{key} - Missing!")
                return False
                
    except json.JSONDecodeError as e:
        print(f"❌ manifest.json - Invalid JSON: {e}")
        return False
    
    print("\n🎉 Installation verification completed successfully!")
    print("\nNext steps:")
    print("1. Restart Home Assistant")
    print("2. Go to Settings → Devices & Services → Add Integration")
    print("3. Search for 'Tududi HACS'")
    print("4. Configure with your Tududi server URL")
    print("5. Optionally add username/password for todo sensors")
    
    return True

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
