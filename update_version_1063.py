#!/usr/bin/env python3
"""Update version.json to v1.0.63 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.63'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.63',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Auto-scroll now scrolls to TOP to show new answers!",
        "FIX: When user scrolled down, new answers appeared at top but scroll stayed at bottom",
        "FIX: Added user scroll state detection - respects manual scrolling",
        "FIX: Scroll state resets on new AI request for fresh auto-scroll behavior",
        "NEW: _setup_scroll_detection() binds to mousewheel and scrollbar events",
        "NEW: _on_manual_scroll() tracks when user manually scrolls",
        "NEW: Auto-scroll disabled message when user manually scrolled",
        "TECHNICAL: ui.py lines 2508-2510 - Changed yview_moveto(1.0) → yview_moveto(0.0)",
        "TECHNICAL: ui.py lines 2497-2500 - Added manual scroll detection",
        "TECHNICAL: ui.py lines 2519-2537 - New scroll detection methods",
        "TECHNICAL: ui.py lines 3877-3879 - Reset scroll state on new AI request",
        "UX: New answers now ALWAYS visible - scroll goes to top where they appear",
        "UX: Respects user's scroll position - won't auto-scroll if manually scrolled",
        "NOTE: Error reporting 'disabled' message is due to old code on Windows (not config issue)",
        "NOTE: Windows PC needs to update to v1.0.61+ to see error reporting status logging"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.63")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🎯 CRITICAL UX IMPROVEMENT:")
print("   1. Auto-scroll now scrolls to TOP (where new answers appear)")
print("   2. Detects user manual scrolling - won't fight user's scroll position")
print("   3. Resets scroll state on new AI request for fresh behavior")
print("   4. Fixes issue where answers never appeared when user scrolled down")
