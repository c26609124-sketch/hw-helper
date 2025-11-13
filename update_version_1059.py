#!/usr/bin/env python3
"""Update version.json to v1.0.59 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.59'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.59',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Telemetry was stuck at v1.0.50 due to hardcoded default!",
        "FIX: Changed version default from '1.0.50' to '0.0.0' (makes failures obvious)",
        "FIX: Added logging to version loading for better debugging",
        "NEW: Error reports now export progressive_answers_container directly!",
        "NEW: progressive_answers_html field captures streaming answers with green highlights",
        "FIX: Removed dependency on last_ai_response check for answer export",
        "NEW: Comprehensive client_secret logging to debug duplicate installation counting",
        "TECHNICAL: ui.py line 1516 - Changed hardcoded version default",
        "TECHNICAL: ui.py lines 300-328 - Export progressive_answers_container first, answer_scroll_frame as fallback",
        "TECHNICAL: lib/api.py lines 27-74 - Added detailed logging for client credential management",
        "NOTE: Telemetry will now report correct version (1.0.59+)",
        "NOTE: Error reports will show actual AI answers with green highlights"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.59")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🎯 THREE MAJOR FIXES:")
print("   1. Telemetry version now reports correctly (was stuck at 1.0.50)")
print("   2. Error reports now capture AI Generated Answers with green highlights")
print("   3. Added detailed logging to debug duplicate installation issue")
