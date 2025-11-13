#!/usr/bin/env python3
"""Update version.json to v1.0.64 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.64'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.64',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Windows 'charmap' codec error when loading version.json!",
        "CRITICAL FIX: Error reporting now works on Windows (UTF-8 encoding added)",
        "FIX: Added encoding='utf-8' to version.json loading (line 1626)",
        "FIX: Added encoding='utf-8' to config.json loading (line 94)",
        "FIX: Windows was using 'charmap' codec which can't decode UTF-8 emoji",
        "NEW: Detailed config loading logging shows what was actually loaded",
        "NEW: Shows 'enabled=True' and endpoint URL when loading config",
        "TECHNICAL: ui.py line 1626 - with open(version_file, 'r', encoding='utf-8')",
        "TECHNICAL: ui.py line 94 - with open(config_path, 'r', encoding='utf-8')",
        "TECHNICAL: ui.py line 100 - Added config loading debug logging",
        "NOTE: This fixes 'charmap codec can't decode byte 0x9d' error on Windows",
        "NOTE: Error reporting 'DISABLED' was caused by encoding error during config load",
        "NOTE: Version.json contains UTF-8 emoji (🎯 📝 ✅) which Windows charmap can't read",
        "NOTE: Both Mac (UTF-8 default) and Windows (charmap default) now work correctly"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.64")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🎯 CRITICAL WINDOWS FIX:")
print("   1. Added UTF-8 encoding to version.json loading (fixes charmap error)")
print("   2. Added UTF-8 encoding to config.json loading (fixes error reporting)")
print("   3. Added detailed logging to show what config was loaded")
print("   4. Error reporting will now work correctly on Windows!")
