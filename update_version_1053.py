#!/usr/bin/env python3
"""Update version.json to v1.0.53 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.53'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.53',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Icons now load correctly from assets/icons/ directory",
        "CRITICAL FIX: Screenshot capture now functional (lib.capture import fixed)",
        "CRITICAL FIX: Error reports now include HTML representation of answers",
        "FIX: Removed unreliable screenshot-based answer capture",
        "FIX: Answer display now exported as clean HTML for error reports",
        "NEW: export_answers_html() function for structured answer export",
        "UPDATE: Error report API no longer uses answer screenshot parameter",
        "UPDATE: Backend receives HTML answers in ai_response_json.answer_html",
        "PERFORMANCE: Faster error reporting (no screenshot rendering)",
        "UX: Error reports display answers properly on admin dashboard"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

# Keep file_hashes from v1.0.52
# (will be regenerated separately)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.53")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
