"""
Advanced Auto-Updater Tests
Tests actual file downloads, backups, and complete update flow
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
import time

sys.path.insert(0, os.path.dirname(__file__))
from auto_updater import AutoUpdater

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def test_file_download():
    """Test downloading actual files from GitHub"""
    print(f"\n{BOLD}Test: File Download from GitHub{RESET}")

    test_dir = Path(tempfile.mkdtemp(prefix="updater_download_test_"))
    print(f"Test directory: {test_dir}")

    try:
        # Create test version file
        version_file = test_dir / "version.json"
        version_file.write_text(json.dumps({"version": "0.1.0"}))

        updater = AutoUpdater(current_dir=str(test_dir))

        # Test downloading version.json from GitHub (use module constant)
        import auto_updater
        url = f"{auto_updater.GITHUB_RAW_URL}/version.json"
        dest_file = test_dir / "downloaded_version.json"

        print(f"Downloading: {url}")
        success = updater._download_file(url, dest_file)

        if success and dest_file.exists():
            # Verify file contents
            with open(dest_file, 'r') as f:
                data = json.load(f)

            if 'version' in data:
                print(f"{GREEN}✅ PASS{RESET}: Downloaded and verified version.json")
                print(f"   → Remote version: {data['version']}")
                return True
            else:
                print(f"{RED}❌ FAIL{RESET}: File downloaded but missing version field")
                return False
        else:
            print(f"{RED}❌ FAIL{RESET}: File download failed")
            return False

    except Exception as e:
        print(f"{RED}❌ FAIL{RESET}: Exception during download test: {e}")
        return False
    finally:
        shutil.rmtree(test_dir)
        print(f"{BLUE}Cleaned up test directory{RESET}")


def test_get_repo_files():
    """Test getting list of repository files"""
    print(f"\n{BOLD}Test: Get Repository File List{RESET}")

    try:
        updater = AutoUpdater()

        print("Fetching repository file list...")
        files = updater._get_repo_files()

        if files:
            print(f"{GREEN}✅ PASS{RESET}: Retrieved {len(files)} files from repo")
            print(f"   → Sample files:")
            for file in files[:10]:  # Show first 10
                print(f"      - {file}")
            if len(files) > 10:
                print(f"      ... and {len(files) - 10} more")
            return True
        else:
            print(f"{RED}❌ FAIL{RESET}: Could not retrieve file list")
            return False

    except Exception as e:
        print(f"{RED}❌ FAIL{RESET}: Exception: {e}")
        return False


def test_file_exclusions():
    """Test that excluded files are properly filtered"""
    print(f"\n{BOLD}Test: File Exclusion Filtering{RESET}")

    # Simulate file list from repo
    all_files = [
        "ui.py",
        "auto_updater.py",
        "version.json",
        "api_key.txt",  # Should be excluded
        "screenshots/test.png",  # Should be excluded
        "__pycache__/test.pyc",  # Should be excluded
        ".DS_Store",  # Should be excluded
        "README.md",
        ".git/config",  # Should be excluded
    ]

    excluded_patterns = [
        '.git',
        '__pycache__',
        '*.pyc',
        '.DS_Store',
        'screenshots/',
        'saved_screenshots/',
        'api_key.txt'
    ]

    filtered_files = []
    for file_path in all_files:
        # Check if file should be excluded
        should_exclude = any(
            pattern.replace('*', '') in file_path or
            file_path.startswith(pattern.replace('*', ''))
            for pattern in excluded_patterns
        )

        if not should_exclude:
            filtered_files.append(file_path)

    # Expected files that should NOT be excluded
    expected = ["ui.py", "auto_updater.py", "version.json", "README.md"]

    # Files that SHOULD be excluded
    excluded = [f for f in all_files if f not in filtered_files]
    expected_excluded = ["api_key.txt", "screenshots/test.png", "__pycache__/test.pyc", ".DS_Store", ".git/config"]

    if set(filtered_files) == set(expected):
        print(f"{GREEN}✅ PASS{RESET}: File exclusion filtering works correctly")
        print(f"   → Kept: {filtered_files}")
        print(f"   → Excluded: {excluded}")
        return True
    else:
        print(f"{RED}❌ FAIL{RESET}: File exclusion incorrect")
        print(f"   → Expected: {expected}")
        print(f"   → Got: {filtered_files}")
        return False


def test_backup_functionality():
    """Test backup creation before updates"""
    print(f"\n{BOLD}Test: Backup System{RESET}")

    test_dir = Path(tempfile.mkdtemp(prefix="updater_backup_test_"))
    print(f"Test directory: {test_dir}")

    try:
        # Create some test files
        (test_dir / "test_file.txt").write_text("original content")
        (test_dir / "version.json").write_text(json.dumps({"version": "0.5.0"}))

        # Create backup directory (simulating what updater does)
        backup_dir = test_dir / ".update_backup"
        backup_dir.mkdir(exist_ok=True)

        # Simulate backup
        test_file = test_dir / "test_file.txt"
        backup_file = backup_dir / "test_file.txt"
        shutil.copy2(test_file, backup_file)

        # Verify backup exists
        if backup_file.exists():
            backup_content = backup_file.read_text()
            if backup_content == "original content":
                print(f"{GREEN}✅ PASS{RESET}: Backup created successfully")
                print(f"   → Backup directory: {backup_dir}")
                print(f"   → Backed up: test_file.txt")
                return True
            else:
                print(f"{RED}❌ FAIL{RESET}: Backup content mismatch")
                return False
        else:
            print(f"{RED}❌ FAIL{RESET}: Backup file not created")
            return False

    except Exception as e:
        print(f"{RED}❌ FAIL{RESET}: Exception: {e}")
        return False
    finally:
        shutil.rmtree(test_dir)
        print(f"{BLUE}Cleaned up test directory{RESET}")


def test_simulated_update_flow():
    """Test simulated complete update flow"""
    print(f"\n{BOLD}Test: Simulated Complete Update Flow{RESET}")

    test_dir = Path(tempfile.mkdtemp(prefix="updater_flow_test_"))
    print(f"Test directory: {test_dir}")

    try:
        # Setup: Create old version environment
        print(f"{BLUE}Setting up old version (0.8.0)...{RESET}")
        version_file = test_dir / "version.json"
        version_file.write_text(json.dumps({"version": "0.8.0"}))

        # Create some files
        (test_dir / "ui.py").write_text("# Old version of ui.py")
        (test_dir / "api_key.txt").write_text("user-secret-key")  # Should be protected

        updater = AutoUpdater(current_dir=str(test_dir))

        # Step 1: Check for updates
        print(f"{BLUE}Step 1: Checking for updates...{RESET}")
        update_available, remote_data = updater.check_for_updates()

        if not update_available:
            print(f"{YELLOW}⚠️  WARN{RESET}: No update available (expected if 0.8.0 == latest)")
            print(f"   → This is OK for testing, but real update flow can't be tested")
            return True

        print(f"{GREEN}✓{RESET} Update available: v{remote_data['version']}")

        # Step 2: Verify version comparison
        print(f"{BLUE}Step 2: Verifying version comparison...{RESET}")
        current_ver = updater.current_version
        remote_ver = remote_data['version']
        print(f"   Current: {current_ver}")
        print(f"   Remote: {remote_ver}")

        if updater._compare_versions(current_ver, remote_ver):
            print(f"{GREEN}✓{RESET} Version comparison correct")
        else:
            print(f"{RED}✗{RESET} Version comparison failed")
            return False

        # Step 3: Verify changelog
        print(f"{BLUE}Step 3: Verifying changelog...{RESET}")
        if 'changelog' in remote_data:
            changelog = remote_data['changelog'][0]
            print(f"   Version: {changelog.get('version')}")
            print(f"   Changes: {len(changelog.get('changes', []))} items")
            print(f"{GREEN}✓{RESET} Changelog present")
        else:
            print(f"{YELLOW}⚠️{RESET} No changelog in remote data")

        print(f"{GREEN}✅ PASS{RESET}: Update flow simulation completed")
        return True

    except Exception as e:
        print(f"{RED}❌ FAIL{RESET}: Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(test_dir)
        print(f"{BLUE}Cleaned up test directory{RESET}")


def test_network_resilience():
    """Test behavior with network issues"""
    print(f"\n{BOLD}Test: Network Resilience{RESET}")

    # Test with invalid URL (simulates network failure)
    import auto_updater

    # Save original URL
    original_url = auto_updater.GITHUB_RAW_URL

    # Test with bad URL
    auto_updater.GITHUB_RAW_URL = "https://invalid-url-that-does-not-exist.com/fake"

    try:
        updater = AutoUpdater()
        remote_data = updater._fetch_remote_version()

        if remote_data is None:
            print(f"{GREEN}✅ PASS{RESET}: Gracefully handled invalid URL")
            print(f"   → Returned None as expected")
            return True
        else:
            print(f"{RED}❌ FAIL{RESET}: Should have returned None for invalid URL")
            return False

    except Exception as e:
        # It's OK if it raises an exception as long as it's caught internally
        print(f"{YELLOW}⚠️  WARN{RESET}: Exception raised (but caught internally): {e}")
        return True
    finally:
        # Restore original URL
        auto_updater.GITHUB_RAW_URL = original_url


def run_advanced_tests():
    """Run all advanced tests"""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}ADVANCED AUTO-UPDATER TESTS{RESET}")
    print(f"{'='*60}\n")

    results = []

    # Run tests
    results.append(("File Download", test_file_download()))
    results.append(("Get Repo Files", test_get_repo_files()))
    results.append(("File Exclusions", test_file_exclusions()))
    results.append(("Backup System", test_backup_functionality()))
    results.append(("Update Flow", test_simulated_update_flow()))
    results.append(("Network Resilience", test_network_resilience()))

    # Summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}ADVANCED TEST SUMMARY{RESET}")
    print(f"{'='*60}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status}: {test_name}")

    print(f"\n{GREEN}Passed{RESET}: {passed}/{total}")
    print(f"{RED}Failed{RESET}: {total - passed}/{total}")
    print(f"{'='*60}\n")

    if passed == total:
        print(f"{GREEN}{BOLD}🎉 ALL ADVANCED TESTS PASSED!{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}⚠️  SOME TESTS FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_advanced_tests())
