#!/usr/bin/env python3
"""Update version.json to v1.0.60 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.60'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.60',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Version loading moved OUT of daemon thread!",
        "FIX: Telemetry now reports correct version (was showing v0.0.0)",
        "FIX: Version loads synchronously during app startup (visible console output)",
        "NEW: Created _load_version() helper method for clean version loading",
        "NEW: Version loaded ONCE at line 1370, before any threads start",
        "REMOVED: 20+ lines of redundant version loading code from telemetry thread",
        "TECHNICAL: ui.py lines 1613-1632 - New _load_version() method",
        "TECHNICAL: ui.py line 1370 - Version loaded synchronously in __init__",
        "TECHNICAL: ui.py lines 1526-1537 - Simplified telemetry thread (no version loading)",
        "NOTE: Print statements from version loading now ALWAYS visible",
        "NOTE: Telemetry will correctly report v1.0.60+",
        "NOTE: If version loading fails, '⚠️ Could not load version' will be visible in console"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.60")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🎯 MAJOR ARCHITECTURAL FIX:")
print("   Version loading moved from daemon thread to synchronous initialization")
print("   - Telemetry will now report correct version (not v0.0.0)")
print("   - All version loading output is visible in console")
print("   - Cleaner, simpler code (20+ lines removed)")
