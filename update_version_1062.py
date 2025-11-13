#!/usr/bin/env python3
"""Update version.json to v1.0.62 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.62'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.62',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Fill blank silent failures now VISIBLE with comprehensive logging!",
        "FIX: Answer ID mismatches now logged instead of silently skipped",
        "FIX: Added '❌ ANSWER ID NOT FOUND' warnings when AI answer can't be mapped",
        "FIX: Empty values now logged with '⚠️ EMPTY VALUE' warning",
        "NEW: Enhanced fuzzy matching strips underscores and prefixes for better ID resolution",
        "NEW: Post-streaming validation checks if blanks still show '???'",
        "NEW: Validation shows which blanks failed and why",
        "NEW: _validate_fill_blank_completeness() method runs after answer processing",
        "TECHNICAL: ui.py lines 4476-4485 - Enhanced fuzzy matching algorithm",
        "TECHNICAL: ui.py lines 4540-4548 - Comprehensive logging for missing answer_ids",
        "TECHNICAL: ui.py lines 4519-4524 - Log empty values in direct_answer processing",
        "TECHNICAL: ui.py lines 4464-4504 - New _validate_fill_blank_completeness() method",
        "TECHNICAL: lib/edmentum.py lines 856-883 - Enhanced update_blank_value logging",
        "NOTE: Now shows answer ID lookup process, successful matches, and failures",
        "NOTE: Validation runs after each batch of answers, showing unfilled blank details",
        "NOTE: This will help debug 'middle blank shows ???' issues"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.62")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🎯 CRITICAL DEBUGGING IMPROVEMENTS:")
print("   1. Fill blank silent failures now visible with comprehensive logging")
print("   2. Answer ID mismatches logged (was silently skipped)")
print("   3. Enhanced fuzzy matching for better ID resolution")
print("   4. Post-streaming validation shows which blanks failed and why")
print("   5. Every update logged with before/after values")
