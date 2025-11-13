#!/usr/bin/env python3
"""Update version.json to v1.0.61 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.61'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.61',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Edmentum components now import correctly!",
        "FIX: 08_fill_blank.png - EdmentumFillBlank now works (was missing from imports)",
        "FIX: 09_sequence.png - EdmentumOrdering now works (was missing from imports)",
        "FIX: 'No module named edmentum_components' error resolved",
        "REMOVED: 4 inline imports that referenced wrong module name",
        "NEW: REMOVED badge support for update modal (gray color)",
        "NEW: CLAUDE.md documentation for development guidelines",
        "NEW: Badge requirements - all badges in changelogs must exist in code",
        "FIX: Added flush=True to all version loading prints (Windows visibility)",
        "FIX: Error reporting status now logs on startup for debugging",
        "TECHNICAL: ui.py lines 47-48 - Added EdmentumFillBlank & EdmentumHotSpot to imports",
        "TECHNICAL: ui.py lines 4281, 4324, 5055, 5085 - Removed inline edmentum_components imports",
        "TECHNICAL: ui.py line 983 - Added REMOVED badge to BADGE_COLORS",
        "TECHNICAL: ui.py lines 1618-1622 - Added flush=True to _load_version() prints",
        "TECHNICAL: ui.py lines 105-107 - Added error reporting status logging",
        "NOTE: This fixes validator errors and 'No answers found' issues",
        "NOTE: Edmentum components (fill blank, ordering, hot spot, hot text) now render properly"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.61")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🎯 CRITICAL FIXES:")
print("   1. Edmentum components now import correctly (fixes 08_fill_blank.png & 09_sequence.png)")
print("   2. Removed 'No module named edmentum_components' error")
print("   3. Added REMOVED badge support")
print("   4. Created CLAUDE.md for development guidelines")
print("   5. Better debugging output (flush=True, error reporting status)")
