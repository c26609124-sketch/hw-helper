#!/usr/bin/env python3
"""Update version.json to v1.0.55 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.55'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.55',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL FIX: Answers no longer disappear when streaming finishes!",
        "FIX: streaming_container now uses selective child destruction",
        "FIX: progressive_answers_container preserved during finalization",
        "TECHNICAL: Replaced .destroy() with selective widget destruction loop"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.55")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
