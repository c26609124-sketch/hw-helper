#!/usr/bin/env python3
"""Update version.json to v1.0.65 with changelog"""

import json
from pathlib import Path
from datetime import datetime

version_file = Path(__file__).parent / "version.json"

with open(version_file, 'r', encoding='utf-8') as f:
    version_data = json.load(f)

# Update version
version_data['version'] = '1.0.65'
version_data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add new changelog
new_changelog = {
    'version': '1.0.65',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [
        "CRITICAL CHANGE: Error reporting now ENABLED by default (opt-out instead of opt-in)!",
        "FIX: Changed error_reporting default from False to True",
        "FIX: Users with old config.json (enabled: false) will now have error reporting work",
        "FIX: Missing config.json now defaults to error reporting enabled",
        "NEW: Error reporting is opt-out - users must explicitly disable it",
        "TECHNICAL: ui.py line 86 - ERROR_REPORTING_ENABLED = True (was False)",
        "TECHNICAL: ui.py line 98 - error_config.get('enabled', True) (was False)",
        "TECHNICAL: ui.py lines 103, 105 - Added 'enabled=True' to default messages",
        "NOTE: This fixes issue where Windows PC had old config with enabled: false",
        "NOTE: All users will now have error reporting enabled unless explicitly disabled",
        "NOTE: To disable error reporting, set 'enabled': false in config.json"
    ]
}

# Insert at beginning
version_data['changelog'].insert(0, new_changelog)

with open(version_file, 'w', encoding='utf-8') as f:
    json.dump(version_data, f, indent=2, ensure_ascii=False)

print("✅ Updated version.json to v1.0.65")
print(f"📝 Added changelog with {len(new_changelog['changes'])} changes")
print("\n🎯 MAJOR POLICY CHANGE:")
print("   1. Error reporting is now OPT-OUT (enabled by default)")
print("   2. Users with old config.json will now have it enabled")
print("   3. Missing config.json defaults to enabled")
print("   4. To disable, users must explicitly set 'enabled': false in config.json")
