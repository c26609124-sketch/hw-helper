#!/usr/bin/env python3
"""Update version.json to v1.0.58 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.58'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.58',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Python f-string syntax error preventing app launch!",
        "FIX: lib/capture.py line 77 - Extracted backslash replacement outside f-string",
        "TECHNICAL: F-strings cannot contain backslash escapes in expression part",
        "TECHNICAL: Changed from f\"name='{path.replace('\\\\', '\\\\\\\\')}' to escaped_path variable",
        "NOTE: This error would have prevented Windows users from launching after v1.0.57 update"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.58")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🚨 SYNTAX FIX: F-string backslash error in lib/capture.py resolved!")
print("   Application can now launch successfully on Windows.")
