"""
Auto-Update System for HW Helper
Checks GitHub for updates and applies them automatically with hash-based differential updates
"""

import json
import os
import sys
import urllib.request
import urllib.error
import shutil
import tempfile
import zipfile
import hashlib
from pathlib import Path
from typing import Optional, Dict, Tuple, List
import logging

# GitHub repository info
GITHUB_USER = "c26609124-sketch"
GITHUB_REPO = "hw-helper"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main"

# Version file path
VERSION_FILE = "version.json"

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoUpdater")


class AutoUpdater:
    """Handles automatic updates from GitHub"""

    def __init__(self, current_dir: Optional[str] = None):
        """
        Initialize the auto-updater

        Args:
            current_dir: Directory containing the application (defaults to script directory)
        """
        self.current_dir = Path(current_dir) if current_dir else Path(__file__).parent
        self.version_file = self.current_dir / VERSION_FILE
        self.current_version = self._load_current_version()

    def _load_current_version(self) -> str:
        """Load current version from version.json"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '0.0.0')
        except Exception as e:
            logger.warning(f"Could not load version file: {e}")

        return "0.0.0"

    def _fetch_remote_version(self) -> Optional[Dict]:
        """
        Fetch version.json from GitHub

        Returns:
            Dict with version info or None if failed
        """
        try:
            url = f"{GITHUB_RAW_URL}/{VERSION_FILE}"
            logger.info(f"Checking for updates at {url}")

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'HW-Helper-AutoUpdater/1.0')
            req.add_header('Cache-Control', 'no-cache')

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data

        except urllib.error.URLError as e:
            logger.error(f"Network error checking for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching remote version: {e}")
            return None

    def _compare_versions(self, current: str, remote: str) -> bool:
        """
        Compare version strings (semantic versioning)

        Args:
            current: Current version (e.g., "1.0.0")
            remote: Remote version (e.g., "1.1.0")

        Returns:
            True if remote is newer, False otherwise
        """
        try:
            current_parts = [int(x) for x in current.split('.')]
            remote_parts = [int(x) for x in remote.split('.')]

            # Pad to same length
            max_len = max(len(current_parts), len(remote_parts))
            current_parts += [0] * (max_len - len(current_parts))
            remote_parts += [0] * (max_len - len(remote_parts))

            return remote_parts > current_parts

        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return False

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of a file

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal hash string
        """
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for {file_path}: {e}")
            return ""

    def _clear_python_cache(self):
        """
        Clear Python bytecode cache files (.pyc) to force reload of updated modules

        This is CRITICAL after updates - without clearing cache, Python will continue
        using old cached .pyc files even though the source .py files have changed.
        """
        logger.info("Clearing Python bytecode cache...")
        cleared_count = 0

        try:
            # Clear __pycache__ directories
            for pycache_dir in self.current_dir.rglob('__pycache__'):
                try:
                    shutil.rmtree(pycache_dir)
                    cleared_count += 1
                    logger.debug(f"  Removed: {pycache_dir}")
                except Exception as e:
                    logger.warning(f"  Could not remove {pycache_dir}: {e}")

            # Clear individual .pyc files in root and lib/
            for pyc_file in self.current_dir.rglob('*.pyc'):
                try:
                    pyc_file.unlink()
                    cleared_count += 1
                    logger.debug(f"  Removed: {pyc_file}")
                except Exception as e:
                    logger.warning(f"  Could not remove {pyc_file}: {e}")

            if cleared_count > 0:
                logger.info(f"✓ Cleared {cleared_count} cache files/directories")
            else:
                logger.debug("No cache files found to clear")

        except Exception as e:
            logger.warning(f"Error clearing Python cache: {e}")

    def check_for_updates(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check if updates are available

        Returns:
            Tuple of (update_available, remote_version_data)
        """
        logger.info(f"Current version: {self.current_version}")

        remote_data = self._fetch_remote_version()
        if not remote_data:
            logger.info("Could not check for updates (no network or repo not found)")
            return False, None

        remote_version = remote_data.get('version', '0.0.0')
        logger.info(f"Remote version: {remote_version}")

        if self._compare_versions(self.current_version, remote_version):
            logger.info(f"Update available: {self.current_version} -> {remote_version}")
            return True, remote_data

        logger.info("Application is up to date")
        return False, None

    def _download_file(self, url: str, dest_path: Path) -> bool:
        """
        Download a file from GitHub

        Args:
            url: URL to download from
            dest_path: Destination file path

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading {url}")

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'HW-Helper-AutoUpdater/1.0')

            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                # Write text files with UTF-8 encoding, binary files as-is
                if dest_path.suffix in ['.py', '.txt', '.md', '.json', '.sh', '.bat']:
                    with open(dest_path, 'w', encoding='utf-8', newline='') as f:
                        f.write(content.decode('utf-8'))
                else:
                    with open(dest_path, 'wb') as f:
                        f.write(content)

            logger.info(f"Downloaded to {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False

    def _get_repo_files(self) -> Optional[list]:
        """
        Get list of all files in the repository

        Returns:
            List of file paths or None if failed
        """
        try:
            url = f"{GITHUB_API_URL}/git/trees/main?recursive=1"

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'HW-Helper-AutoUpdater/1.0')
            req.add_header('Accept', 'application/vnd.github.v3+json')

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())

                # Extract file paths (exclude directories)
                files = [
                    item['path']
                    for item in data.get('tree', [])
                    if item['type'] == 'blob'
                ]

                return files

        except Exception as e:
            logger.error(f"Error getting repo files: {e}")
            return None

    def download_update(self, remote_version_data: Optional[Dict] = None, progress_callback=None) -> bool:
        """
        Download update files from GitHub (hash-based differential update)

        Args:
            remote_version_data: Remote version data with file_hashes (from version.json)
            progress_callback: Optional callback function(current, total, filename, percentage)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get remote file hashes
            remote_hashes = {}
            if remote_version_data:
                remote_hashes = remote_version_data.get('file_hashes', {})

            # If no hashes available, fall back to downloading all files
            if not remote_hashes:
                logger.warning("No file hashes in version.json - downloading all files")
                files_to_update = self._get_repo_files()
                if not files_to_update:
                    logger.error("Could not get list of files to update")
                    return False
            else:
                # Hash-based comparison - only download changed files
                files_to_update = list(remote_hashes.keys())

            # Filter out files we don't want to overwrite
            excluded_patterns = [
                '.git',
                '__pycache__',
                '*.pyc',
                '.DS_Store',
                'screenshots/',
                'saved_screenshots/',
                'api_key.txt',  # Don't overwrite user's API key
                'config.json'  # Don't overwrite user's config
            ]

            files_to_download = []
            for file_path in files_to_update:
                # Skip excluded patterns
                if any(pattern.replace('*', '') in file_path or file_path.startswith(pattern.replace('*', ''))
                       for pattern in excluded_patterns):
                    continue

                # If hashes available, compare local vs remote
                if remote_hashes and file_path in remote_hashes:
                    local_path = self.current_dir / file_path
                    remote_hash = remote_hashes[file_path]

                    # Download if file missing OR hash differs
                    if not local_path.exists():
                        files_to_download.append(file_path)
                        logger.info(f"  New file: {file_path}")
                    else:
                        local_hash = self._compute_file_hash(local_path)
                        if local_hash != remote_hash:
                            files_to_download.append(file_path)
                            logger.info(f"  Changed: {file_path}")
                        else:
                            logger.debug(f"  Unchanged: {file_path}")
                else:
                    # No hash info - download file
                    files_to_download.append(file_path)

            logger.info(f"Downloading {len(files_to_download)}/{len(files_to_update)} changed files...")

            # Create backup directory
            backup_dir = self.current_dir / '.update_backup'
            backup_dir.mkdir(exist_ok=True)

            # Download and apply updates
            success_count = 0
            total_files = len(files_to_download)

            for index, file_path in enumerate(files_to_download, 1):
                url = f"{GITHUB_RAW_URL}/{file_path}"
                dest_path = self.current_dir / file_path

                # Report progress
                if progress_callback:
                    percentage = int((index / total_files) * 100)
                    progress_callback(index, total_files, file_path, percentage)

                # Backup existing file
                if dest_path.exists():
                    backup_path = backup_dir / file_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(dest_path, backup_path)

                # Download new version
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                if self._download_file(url, dest_path):
                    success_count += 1
                else:
                    logger.warning(f"Failed to download {file_path}")

            logger.info(f"Successfully updated {success_count}/{len(files_to_download)} files")

            # CRITICAL: Clear Python bytecode cache to force reload of updated .py files
            # Without this, Python will use cached .pyc files even though source changed
            if success_count > 0:
                self._clear_python_cache()

            # Clean up old backup (keep only latest)
            try:
                shutil.rmtree(backup_dir)
            except:
                pass

            return success_count > 0

        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return False

    def apply_update(self, progress_callback=None) -> bool:
        """
        Check for and apply updates (with hash-based differential download)

        Args:
            progress_callback: Optional callback function(current, total, filename, percentage)

        Returns:
            True if update was applied, False otherwise
        """
        update_available, remote_data = self.check_for_updates()

        if not update_available:
            return False

        logger.info("Applying update...")

        if self.download_update(remote_version_data=remote_data, progress_callback=progress_callback):
            logger.info("Update applied successfully!")
            logger.info(f"Updated to version {remote_data['version']}")

            # Show changelog if available
            if 'changelog' in remote_data and remote_data['changelog']:
                latest_changelog = remote_data['changelog'][0]
                logger.info("\nWhat's new:")
                for change in latest_changelog.get('changes', []):
                    logger.info(f"  - {change}")

            return True

        logger.error("Failed to apply update")
        return False


def check_for_updates_silent() -> Tuple[bool, Optional[str], Optional[list]]:
    """
    Check for updates without logging (for UI integration)

    Returns:
        Tuple of (update_available, new_version, changelog)
    """
    updater = AutoUpdater()
    update_available, remote_data = updater.check_for_updates()

    if update_available and remote_data:
        new_version = remote_data.get('version', 'unknown')
        changelog = remote_data.get('changelog', [{}])[0].get('changes', [])
        return True, new_version, changelog

    return False, None, None


def apply_update_silent(progress_callback=None) -> bool:
    """
    Apply updates without logging (for UI integration)

    Args:
        progress_callback: Optional callback function(current, total, filename, percentage)

    Returns:
        True if update applied successfully
    """
    updater = AutoUpdater()
    return updater.apply_update(progress_callback=progress_callback)


if __name__ == "__main__":
    # CLI usage
    updater = AutoUpdater()

    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Just check, don't apply
        update_available, remote_data = updater.check_for_updates()
        if update_available:
            print(f"Update available: {remote_data['version']}")
            sys.exit(0)
        else:
            print("No updates available")
            sys.exit(1)
    else:
        # Check and apply
        if updater.apply_update():
            print("Update completed! Please restart the application.")
            sys.exit(0)
        else:
            print("No updates applied")
            sys.exit(1)
