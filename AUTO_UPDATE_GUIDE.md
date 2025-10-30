# Auto-Update System Guide

## Overview

The HW Helper application now includes an automatic update system that keeps all users on the latest version without manual intervention.

**Repository**: https://github.com/c26609124-sketch/hw-helper

## How It Works

### For End Users

1. **Automatic Checks**: Every time users start the application, it automatically checks GitHub for updates
2. **Update Notification**: If an update is available, users see:
   - New version number
   - What's new (changelog)
   - Download progress
3. **One-Click Apply**: Updates download and install automatically
4. **Restart Required**: Users simply restart the app to use the new version

### For Developers (You)

When you want to push an update to all users:

## Pushing Updates

### Step 1: Make Your Changes

Edit any files you need to update (ui.py, components, etc.)

### Step 2: Update Version Number

Edit `version.json`:

```json
{
  "version": "1.1.0",  ← Increment this (1.0.0 → 1.1.0)
  "release_date": "2025-10-30",
  "changelog": [
    {
      "version": "1.1.0",
      "date": "2025-10-30",
      "changes": [
        "Added new feature X",
        "Fixed bug Y",
        "Improved performance of Z"
      ]
    },
    ... keep old versions below
  ]
}
```

**Version Numbering**:
- **Major**: 1.0.0 → 2.0.0 (breaking changes)
- **Minor**: 1.0.0 → 1.1.0 (new features)
- **Patch**: 1.0.0 → 1.0.1 (bug fixes)

### Step 3: Commit and Push

```bash
cd "/Users/admin/Downloads/HW Helper copy 2"

# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "v1.1.0: Added feature X, fixed bug Y"

# Push to GitHub
git push origin main
```

### Step 4: Automatic Distribution

**That's it!** All users will automatically receive the update the next time they start the app.

## How Users Get Updates

```
User starts app
     ↓
App checks GitHub (version.json)
     ↓
Compares local (1.0.0) vs remote (1.1.0)
     ↓
Update available! ✅
     ↓
Downloads updated files from GitHub
     ↓
Applies changes to local installation
     ↓
User restarts app
     ↓
Now running v1.1.0 ✅
```

## Testing Updates

### Before Pushing to Production

1. **Test Locally**: Make sure your changes work
2. **Update version.json**: Increment version number
3. **Test Update Flow**:
   ```bash
   # Temporarily change local version to test
   python3 -c "
   from auto_updater import check_for_updates_silent
   available, version, changelog = check_for_updates_silent()
   print(f'Update available: {available}')
   print(f'New version: {version}')
   "
   ```
4. **Push to GitHub**: `git push origin main`
5. **Verify**: Open app on a different machine/folder and check for update

## Files Protected from Updates

The following files are **NOT** overwritten during updates (user data preserved):

- `api_key.txt` - User's API key
- `screenshots/` - Saved screenshots
- `saved_screenshots/` - Saved screenshots
- `*.png, *.jpg` - Image files
- `.git/` - Git repository data

## Update System Architecture

### Files
- **`auto_updater.py`**: Core update module
- **`version.json`**: Version tracking and changelog
- **`ui.py`** (lines 53-59, 477-627): Integration into main app

### How It Works
1. **On Startup**: Thread checks GitHub for latest version.json
2. **Version Compare**: Semantic versioning comparison (1.0.0 vs 1.1.0)
3. **Download**: Fetches updated files from GitHub raw URL
4. **Backup**: Creates `.update_backup/` with old files
5. **Apply**: Overwrites files with new versions
6. **Restart**: User restarts to load new code

## Troubleshooting

### "Could not check for updates (no network or repo not found)"

**Cause**: Network issue or GitHub repo not accessible

**Solutions**:
- Check internet connection
- Verify repo URL: https://github.com/c26609124-sketch/hw-helper
- Make sure repo is public (not private)

### "Update download failed"

**Cause**: Network interruption during download

**Solution**:
- App will retry on next startup
- Users can manually check by restarting

### Users Not Getting Updates

**Checklist**:
- [ ] Version number incremented in version.json?
- [ ] Changes committed to git?
- [ ] Pushed to GitHub (`git push origin main`)?
- [ ] Repo is public (not private)?
- [ ] Users have internet connection?

## Advanced: Manual Update Script

If you want to create a one-time update script:

```python
# manual_update.py
from auto_updater import apply_update_silent

if apply_update_silent():
    print("Update completed! Restart the app.")
else:
    print("No updates available or update failed.")
```

## GitHub Repository Info

- **URL**: https://github.com/c26609124-sketch/hw-helper
- **Owner**: c26609124-sketch
- **Branch**: main
- **Access**: Public (anyone can download)

## Security Notes

1. **Token Already Used**: The GitHub token was embedded during initial push
2. **Public Repo**: Anyone can view the code
3. **Safe for Users**: Updates only download from official repository
4. **No API Key Overwrite**: User's api_key.txt is protected

## Future Updates Example

### Example: Fixing a Bug

```bash
# 1. Fix the bug in your code
nano ui.py  # Make your changes

# 2. Update version.json
nano version.json
# Change version: "1.0.0" → "1.0.1"
# Add to changelog: "Fixed issue with button X"

# 3. Push to GitHub
git add -A
git commit -m "v1.0.1: Fixed button X issue"
git push origin main

# 4. Done! Users get update on next app start
```

### Example: Adding a Feature

```bash
# 1. Add your feature
nano ui.py  # Add new feature

# 2. Update version.json
# Change version: "1.0.0" → "1.1.0"
# Add to changelog: "Added feature Y for better user experience"

# 3. Push to GitHub
git add -A
git commit -m "v1.1.0: Added feature Y"
git push origin main

# 4. Users automatically receive the new feature!
```

## Summary

✅ **For You**: Just update version.json and push to GitHub
✅ **For Users**: Automatic updates on app startup
✅ **Distribution**: Instant to all users
✅ **Safe**: Backups created, user data protected
✅ **Simple**: No manual downloads or installations needed

---

**Questions?**
- Check `auto_updater.py` for implementation details
- Review `ui.py` lines 477-627 for integration
- See HOT_TEXT_FIXES.md for recent updates

**Ready to Push Your First Update?**
1. Make your changes
2. Edit version.json
3. `git add -A && git commit -m "v1.X.X: Your changes" && git push origin main`
4. Done!
