#!/usr/bin/env python3
"""Update version.json to v1.0.57 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.57'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.57',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Auto-updater now downloads to CORRECT directory (project root)!",
        "CRITICAL FIX: Updater was downloading to lib/ instead of project root since v1.0.52",
        "FIX: Changed AutoUpdater default from .parent to .parent.parent",
        "FIX: check_for_updates_silent now explicitly passes project root",
        "FIX: apply_update_silent now explicitly passes project root",
        "TECHNICAL: lib/updater.py line 44 - Added .parent.parent for correct path resolution",
        "TECHNICAL: lib/updater.py lines 417 & 440 - Explicit project_root parameters",
        "NOTE: All fixes from v1.0.53-v1.0.56 will NOW be properly applied",
        "NOTE: This explains why icons/capture errors persisted despite version showing 1.0.56"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.57")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🚨 EMERGENCY FIX: Updater was downloading to wrong directory!")
print("   This fix will finally apply all previous updates correctly.")
