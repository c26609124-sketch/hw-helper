#!/usr/bin/env python3
"""Update version.json to v1.0.56 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.56'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.56',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Auto-updater now clears Python bytecode cache (.pyc files)",
        "FIX: Updates now properly reload code instead of using stale cached files",
        "NEW: TECHNICAL badge support in update modal (gray color)",
        "TECHNICAL: Added _clear_python_cache() method to AutoUpdater",
        "TECHNICAL: Clears __pycache__ directories and .pyc files after successful update",
        "UX: Users will now see actual updated code, not cached versions"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.56")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
