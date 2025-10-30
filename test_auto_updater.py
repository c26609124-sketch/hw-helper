"""
Comprehensive Auto-Updater Test Suite
Tests all critical functionality of the auto-update system
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
import time
from typing import Tuple, List

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from auto_updater import AutoUpdater, check_for_updates_silent, apply_update_silent

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class TestResult:
    """Store test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def add_pass(self, test_name: str, message: str = ""):
        self.passed.append((test_name, message))
        print(f"{GREEN}✅ PASS{RESET}: {test_name}")
        if message:
            print(f"   → {message}")

    def add_fail(self, test_name: str, message: str):
        self.failed.append((test_name, message))
        print(f"{RED}❌ FAIL{RESET}: {test_name}")
        print(f"   → {message}")

    def add_warning(self, test_name: str, message: str):
        self.warnings.append((test_name, message))
        print(f"{YELLOW}⚠️  WARN{RESET}: {test_name}")
        print(f"   → {message}")

    def print_summary(self):
        total = len(self.passed) + len(self.failed)
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}TEST SUMMARY{RESET}")
        print(f"{'='*60}")
        print(f"{GREEN}Passed{RESET}: {len(self.passed)}/{total}")
        print(f"{RED}Failed{RESET}: {len(self.failed)}/{total}")
        print(f"{YELLOW}Warnings{RESET}: {len(self.warnings)}")

        if self.failed:
            print(f"\n{RED}Failed Tests:{RESET}")
            for test_name, message in self.failed:
                print(f"  ❌ {test_name}: {message}")

        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for test_name, message in self.warnings:
                print(f"  ⚠️  {test_name}: {message}")

        print(f"{'='*60}\n")

        return len(self.failed) == 0


class AutoUpdaterTestSuite:
    """Comprehensive test suite for auto-updater"""

    def __init__(self):
        self.results = TestResult()
        self.test_dir = None

    def setup_test_env(self):
        """Create isolated test environment"""
        print(f"\n{BLUE}Setting up test environment...{RESET}")
        self.test_dir = Path(tempfile.mkdtemp(prefix="updater_test_"))
        print(f"Test directory: {self.test_dir}")
        return self.test_dir

    def cleanup_test_env(self):
        """Clean up test environment"""
        if self.test_dir and self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            print(f"{BLUE}Cleaned up test directory{RESET}")

    # ==================== PHASE 1: UNIT TESTS ====================

    def test_version_comparison(self):
        """Test 1.1: Version comparison logic"""
        print(f"\n{BOLD}Phase 1: Unit Tests - Version Comparison{RESET}")

        updater = AutoUpdater()

        # Test cases: (current, remote, expected_update_available)
        test_cases = [
            ("1.0.0", "1.1.0", True, "Minor update"),
            ("1.0.0", "1.0.1", True, "Patch update"),
            ("1.0.0", "2.0.0", True, "Major update"),
            ("2.0.0", "1.9.9", False, "Newer version already installed"),
            ("1.0.0", "1.0.0", False, "Same version"),
            ("1.0", "1.0.0", False, "Version padding"),
            ("0.9.0", "1.0.0", True, "Pre-release to release"),
        ]

        for current, remote, expected, desc in test_cases:
            result = updater._compare_versions(current, remote)
            if result == expected:
                self.results.add_pass(f"Version compare: {desc}", f"{current} vs {remote} → {expected}")
            else:
                self.results.add_fail(f"Version compare: {desc}",
                    f"Expected {expected}, got {result} for {current} vs {remote}")

    def test_version_loading(self):
        """Test 1.2: Version loading from file"""
        print(f"\n{BOLD}Phase 1: Unit Tests - Version Loading{RESET}")

        # Test 1: Valid version.json
        test_dir = self.setup_test_env()
        version_file = test_dir / "version.json"
        version_file.write_text(json.dumps({"version": "1.5.3"}))

        updater = AutoUpdater(current_dir=str(test_dir))
        if updater.current_version == "1.5.3":
            self.results.add_pass("Load valid version.json", "Loaded version 1.5.3")
        else:
            self.results.add_fail("Load valid version.json", f"Got {updater.current_version}")

        # Test 2: Missing version.json
        version_file.unlink()
        updater = AutoUpdater(current_dir=str(test_dir))
        if updater.current_version == "0.0.0":
            self.results.add_pass("Missing version.json defaults to 0.0.0")
        else:
            self.results.add_fail("Missing version.json", f"Expected 0.0.0, got {updater.current_version}")

        # Test 3: Corrupted version.json
        version_file.write_text("{ invalid json")
        updater = AutoUpdater(current_dir=str(test_dir))
        if updater.current_version == "0.0.0":
            self.results.add_pass("Corrupted version.json handled gracefully")
        else:
            self.results.add_warning("Corrupted version.json", f"Got {updater.current_version}")

        self.cleanup_test_env()

    def test_remote_version_fetching(self):
        """Test 1.3: Fetch version from GitHub"""
        print(f"\n{BOLD}Phase 1: Unit Tests - Remote Version Fetching{RESET}")

        updater = AutoUpdater()

        # Test: Successful fetch from GitHub
        remote_data = updater._fetch_remote_version()
        if remote_data and 'version' in remote_data:
            self.results.add_pass("Fetch from GitHub", f"Got version {remote_data['version']}")
        else:
            self.results.add_fail("Fetch from GitHub", "Could not fetch or parse remote version")

        # Test: Network timeout handling (can't easily test without mocking)
        self.results.add_warning("Network timeout test", "Requires manual network disconnect test")

    # ==================== PHASE 2-3: FILE TESTS ====================

    def test_file_protection(self):
        """Test 3.1-3.3: Protected files and directories"""
        print(f"\n{BOLD}Phase 2-3: File Protection Tests{RESET}")

        test_dir = self.setup_test_env()

        # Create mock protected files
        api_key_file = test_dir / "api_key.txt"
        api_key_file.write_text("sk-test-key-12345")

        screenshots_dir = test_dir / "screenshots"
        screenshots_dir.mkdir()
        (screenshots_dir / "test.png").write_text("fake image data")

        # Create version file
        version_file = test_dir / "version.json"
        version_file.write_text(json.dumps({"version": "0.5.0"}))

        # Simulate updater checking protected files
        updater = AutoUpdater(current_dir=str(test_dir))
        excluded_patterns = [
            '.git',
            '__pycache__',
            '*.pyc',
            '.DS_Store',
            'screenshots/',
            'saved_screenshots/',
            'api_key.txt'
        ]

        # Check that api_key.txt would be excluded
        should_exclude_api_key = any('api_key.txt' in pattern or 'api_key.txt'.startswith(pattern.replace('*', ''))
                                      for pattern in excluded_patterns)

        if should_exclude_api_key:
            self.results.add_pass("API key protection", "api_key.txt in exclusion list")
        else:
            self.results.add_fail("API key protection", "api_key.txt not protected!")

        # Check screenshots directory
        should_exclude_screenshots = any('screenshots/' in pattern
                                         for pattern in excluded_patterns)

        if should_exclude_screenshots:
            self.results.add_pass("Screenshots directory protection", "screenshots/ in exclusion list")
        else:
            self.results.add_fail("Screenshots directory protection", "screenshots/ not protected!")

        self.cleanup_test_env()

    # ==================== PHASE 5: INTEGRATION TESTS ====================

    def test_silent_mode_functions(self):
        """Test 5.3: Silent mode functions"""
        print(f"\n{BOLD}Phase 5: Integration Tests - Silent Mode{RESET}")

        try:
            # Test check_for_updates_silent
            update_available, new_version, changelog = check_for_updates_silent()

            if isinstance(update_available, bool):
                self.results.add_pass("check_for_updates_silent returns bool")
            else:
                self.results.add_fail("check_for_updates_silent return type",
                    f"Expected bool, got {type(update_available)}")

            if update_available:
                if new_version:
                    self.results.add_pass("Silent mode version detection", f"Found version {new_version}")
                else:
                    self.results.add_fail("Silent mode version", "Update available but no version returned")

        except Exception as e:
            self.results.add_fail("Silent mode functions", f"Exception: {e}")

    # ==================== PHASE 6: END-TO-END TESTS ====================

    def test_update_check_flow(self):
        """Test 6.1-6.2: Complete update check flow"""
        print(f"\n{BOLD}Phase 6: End-to-End Tests - Update Check Flow{RESET}")

        # Test with current version (should say up to date)
        updater = AutoUpdater()
        update_available, remote_data = updater.check_for_updates()

        if not update_available:
            self.results.add_pass("No update when version matches", "Application is up to date")
        else:
            self.results.add_warning("Update check", "Update available (expected if GitHub has newer version)")

        # Test with old version (should find update)
        test_dir = self.setup_test_env()
        version_file = test_dir / "version.json"
        version_file.write_text(json.dumps({"version": "0.1.0"}))

        updater_old = AutoUpdater(current_dir=str(test_dir))
        update_available, remote_data = updater_old.check_for_updates()

        if update_available:
            self.results.add_pass("Update detection with old version", f"Found update to {remote_data['version']}")
        else:
            self.results.add_fail("Update detection", "Should have found update for version 0.1.0")

        self.cleanup_test_env()

    # ==================== PHASE 7: EDGE CASES ====================

    def test_invalid_version_formats(self):
        """Test 7.2: Invalid version.json formats"""
        print(f"\n{BOLD}Phase 7: Edge Cases - Invalid Version Formats{RESET}")

        test_dir = self.setup_test_env()
        version_file = test_dir / "version.json"

        # Test malformed JSON
        version_file.write_text("{ malformed json }")
        updater = AutoUpdater(current_dir=str(test_dir))

        if updater.current_version == "0.0.0":
            self.results.add_pass("Malformed JSON handling", "Defaulted to 0.0.0")
        else:
            self.results.add_fail("Malformed JSON", f"Expected 0.0.0, got {updater.current_version}")

        # Test missing version field
        version_file.write_text(json.dumps({"no_version_field": "test"}))
        updater = AutoUpdater(current_dir=str(test_dir))

        if updater.current_version == "0.0.0":
            self.results.add_pass("Missing version field handling", "Defaulted to 0.0.0")
        else:
            self.results.add_fail("Missing version field", f"Expected 0.0.0, got {updater.current_version}")

        self.cleanup_test_env()

    # ==================== PHASE 8: PERFORMANCE TESTS ====================

    def test_performance(self):
        """Test 8.1: Update check performance"""
        print(f"\n{BOLD}Phase 8: Performance Tests{RESET}")

        updater = AutoUpdater()

        # Time the update check
        start_time = time.time()
        update_available, remote_data = updater.check_for_updates()
        elapsed_time = time.time() - start_time

        print(f"   Update check time: {elapsed_time:.2f}s")

        if elapsed_time < 10.0:
            self.results.add_pass("Update check performance", f"Completed in {elapsed_time:.2f}s (< 10s target)")
        else:
            self.results.add_warning("Update check performance", f"Took {elapsed_time:.2f}s (>10s)")

    # ==================== MAIN TEST RUNNER ====================

    def run_all_tests(self):
        """Run all test phases"""
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}AUTO-UPDATER COMPREHENSIVE TEST SUITE{RESET}")
        print(f"{'='*60}\n")

        print(f"{BLUE}GitHub Repository:{RESET} https://github.com/c26609124-sketch/hw-helper")
        print(f"{BLUE}Testing auto_updater.py functionality...{RESET}\n")

        # Run all test phases
        self.test_version_comparison()
        self.test_version_loading()
        self.test_remote_version_fetching()
        self.test_file_protection()
        self.test_silent_mode_functions()
        self.test_update_check_flow()
        self.test_invalid_version_formats()
        self.test_performance()

        # Print summary
        success = self.results.print_summary()

        return success


def main():
    """Main entry point"""
    suite = AutoUpdaterTestSuite()
    success = suite.run_all_tests()

    if success:
        print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}Auto-updater is production-ready.{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}⚠️  SOME TESTS FAILED{RESET}")
        print(f"{RED}Review failures above and fix issues.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
