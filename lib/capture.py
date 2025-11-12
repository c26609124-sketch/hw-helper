"""
Screenshot Capture Module with ChromeDriver Auto-Installation
==============================================================
Selenium-based screenshot capture for Brave/Chrome browser with:
- Remote debugging connection
- Iframe content extraction
- Dropdown option detection
- ChromeDriver automatic download and installation

This module automatically detects your Brave/Chrome version and downloads
the matching ChromeDriver binary from Google's official API.
"""

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException,
    StaleElementReferenceException, NoSuchWindowException
)
import time
import os
import sys
import platform
import subprocess
import zipfile
import urllib.request
import urllib.error
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image
import base64
import traceback


# ============================================================================
# CHROMEDRIVER AUTO-INSTALLATION
# ============================================================================

# ChromeDriver storage directory
CHROMEDRIVER_DIR = Path.home() / ".hwhelper" / "drivers"
CHROMEDRIVER_DIR.mkdir(parents=True, exist_ok=True)

# Google Chrome for Testing API
CHROME_VERSIONS_API = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"


def get_brave_version() -> Optional[str]:
    """
    Detect the installed Brave browser version

    Returns:
        Version string (e.g., "131.0.6778.85") or None if not found
    """
    system = platform.system()

    try:
        if system == "Windows":
            # Check common Brave installation paths
            paths = [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]

            for brave_path in paths:
                if os.path.exists(brave_path):
                    # Get file version using wmic
                    # Extract path replacement outside f-string (backslashes not allowed in f-string expressions)
                    escaped_path = brave_path.replace('\\', '\\\\')
                    result = subprocess.run(
                        ['wmic', 'datafile', 'where', f"name='{escaped_path}'", 'get', 'Version'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) >= 2:
                            version = lines[1].strip()
                            if version:
                                print(f"✓ Detected Brave version: {version}")
                                return version

        elif system == "Darwin":  # macOS
            brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
            if os.path.exists(brave_path):
                result = subprocess.run(
                    [brave_path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # Output format: "Brave Browser 131.0.6778.85"
                    parts = result.stdout.strip().split()
                    if len(parts) >= 3:
                        version = parts[-1]
                        print(f"✓ Detected Brave version: {version}")
                        return version

        elif system == "Linux":
            # Try brave-browser or brave command
            for cmd in ['brave-browser', 'brave']:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    parts = result.stdout.strip().split()
                    if len(parts) >= 2:
                        version = parts[-1]
                        print(f"✓ Detected Brave version: {version}")
                        return version

    except Exception as e:
        print(f"⚠️ Error detecting Brave version: {e}")

    print("⚠️ Could not detect Brave version automatically")
    return None


def get_matching_chromedriver_url(brave_version: str) -> Optional[str]:
    """
    Find the matching ChromeDriver download URL for a given Brave/Chrome version

    Args:
        brave_version: Version string (e.g., "131.0.6778.85")

    Returns:
        Download URL for the matching ChromeDriver binary, or None if not found
    """
    try:
        print(f"🔍 Looking for ChromeDriver matching Brave {brave_version}...")

        # Fetch the versions JSON from Google's API
        req = urllib.request.Request(CHROME_VERSIONS_API)
        req.add_header('User-Agent', 'HW-Helper-ChromeDriver-Installer/1.0')

        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))

        versions = data.get('versions', [])
        if not versions:
            print("⚠️ No versions found in Chrome for Testing API")
            return None

        # Extract major version from Brave version (e.g., "131" from "131.0.6778.85")
        major_version = brave_version.split('.')[0]

        # Determine platform
        system = platform.system()
        if system == "Windows":
            platform_key = "win64"
        elif system == "Darwin":
            # Check if Apple Silicon (M1/M2) or Intel
            machine = platform.machine().lower()
            if 'arm' in machine or 'aarch64' in machine:
                platform_key = "mac-arm64"
            else:
                platform_key = "mac-x64"
        elif system == "Linux":
            platform_key = "linux64"
        else:
            print(f"⚠️ Unsupported platform: {system}")
            return None

        # Find the best matching version
        # Strategy: Find versions with same major version, pick the closest one
        matching_versions = []
        for version_entry in versions:
            version = version_entry.get('version', '')
            if version.startswith(major_version + '.'):
                matching_versions.append(version_entry)

        if not matching_versions:
            print(f"⚠️ No ChromeDriver found for version {major_version}.x")
            return None

        # Pick the closest match (ideally exact, or the latest in the major version)
        best_match = None
        for version_entry in matching_versions:
            if version_entry['version'] == brave_version:
                # Exact match found!
                best_match = version_entry
                break
            elif not best_match or version_entry['version'] > best_match['version']:
                # Keep track of the latest version in this major series
                best_match = version_entry

        if not best_match:
            return None

        # Extract ChromeDriver download URL for this platform
        downloads = best_match.get('downloads', {})
        chromedriver_list = downloads.get('chromedriver', [])

        for download_entry in chromedriver_list:
            if download_entry.get('platform') == platform_key:
                url = download_entry.get('url')
                print(f"✓ Found ChromeDriver {best_match['version']} for {platform_key}")
                return url

        print(f"⚠️ No ChromeDriver download found for platform {platform_key}")
        return None

    except Exception as e:
        print(f"❌ Error fetching ChromeDriver URL: {e}")
        traceback.print_exc()
        return None


def download_and_install_chromedriver(url: str) -> Optional[str]:
    """
    Download and install ChromeDriver from the given URL

    Args:
        url: Download URL for ChromeDriver zip file

    Returns:
        Path to the installed chromedriver binary, or None if failed
    """
    try:
        print(f"⬇️ Downloading ChromeDriver from {url}")

        # Create temp download path
        temp_zip = CHROMEDRIVER_DIR / "chromedriver_temp.zip"
        temp_extract = CHROMEDRIVER_DIR / "chromedriver_extract"

        # Download the zip file
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'HW-Helper-ChromeDriver-Installer/1.0')

        with urllib.request.urlopen(req, timeout=60) as response:
            with open(temp_zip, 'wb') as f:
                f.write(response.read())

        print(f"✓ Downloaded to {temp_zip}")

        # Extract the zip file
        print("📦 Extracting ChromeDriver...")
        if temp_extract.exists():
            shutil.rmtree(temp_extract)
        temp_extract.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)

        # Find the chromedriver binary in the extracted files
        chromedriver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
        chromedriver_binary = None

        for root, dirs, files in os.walk(temp_extract):
            if chromedriver_name in files:
                chromedriver_binary = Path(root) / chromedriver_name
                break

        if not chromedriver_binary or not chromedriver_binary.exists():
            print(f"❌ Could not find {chromedriver_name} in extracted files")
            return None

        # Move to final location
        final_path = CHROMEDRIVER_DIR / chromedriver_name
        if final_path.exists():
            final_path.unlink()  # Remove old version

        shutil.move(str(chromedriver_binary), str(final_path))

        # Make executable on Unix systems
        if platform.system() != "Windows":
            os.chmod(final_path, 0o755)

        print(f"✓ ChromeDriver installed to {final_path}")

        # Cleanup
        if temp_zip.exists():
            temp_zip.unlink()
        if temp_extract.exists():
            shutil.rmtree(temp_extract)

        return str(final_path)

    except Exception as e:
        print(f"❌ Error installing ChromeDriver: {e}")
        traceback.print_exc()
        return None


def verify_chromedriver(driver_path: str) -> bool:
    """
    Verify that the ChromeDriver binary works

    Args:
        driver_path: Path to chromedriver binary

    Returns:
        True if chromedriver works, False otherwise
    """
    try:
        # Try to get version
        result = subprocess.run(
            [driver_path, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            version_output = result.stdout.strip()
            print(f"✓ ChromeDriver verified: {version_output}")
            return True
        else:
            print(f"❌ ChromeDriver verification failed with code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error verifying ChromeDriver: {e}")
        return False


def get_or_install_chromedriver() -> Optional[str]:
    """
    Get ChromeDriver path, installing it automatically if needed

    Returns:
        Path to chromedriver binary, or None if failed
    """
    # Check if ChromeDriver already exists in .hwhelper/drivers/
    chromedriver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
    existing_driver = CHROMEDRIVER_DIR / chromedriver_name

    if existing_driver.exists():
        # Verify it works
        if verify_chromedriver(str(existing_driver)):
            print(f"✓ Using existing ChromeDriver: {existing_driver}")
            return str(existing_driver)
        else:
            print("⚠️ Existing ChromeDriver failed verification, will reinstall")
            existing_driver.unlink()

    # Auto-detect Brave version
    brave_version = get_brave_version()
    if not brave_version:
        print("❌ Could not detect Brave version for ChromeDriver installation")
        return None

    # Find matching ChromeDriver URL
    download_url = get_matching_chromedriver_url(brave_version)
    if not download_url:
        print("❌ Could not find matching ChromeDriver download")
        return None

    # Download and install
    driver_path = download_and_install_chromedriver(download_url)
    if not driver_path:
        print("❌ Failed to download and install ChromeDriver")
        return None

    # Verify installation
    if not verify_chromedriver(driver_path):
        print("❌ Newly installed ChromeDriver failed verification")
        return None

    return driver_path


# ============================================================================
# SCREENSHOT CAPTURE (from selenium_capture_logic.py)
# ============================================================================

# Configuration
DEBUGGING_PORT = 9222
TARGET_TAB_URL_CONTAINS = "edmentum.com"
TARGET_TAB_TITLE_CONTAINS = ""
MAIN_CONTAINER_LOCATOR_STRATEGY = By.CLASS_NAME
MAIN_CONTAINER_LOCATOR_VALUE = "content-wrapper"
IFRAME_ID = "content-iframe"

SCREENSHOT_FILENAME = "final_content_shot.png"

VIEWPORT_EMULATION_PADDING = 20
DEVICE_SCALE_FACTOR = 1.0

DROPDOWN_PARENT_SELECTOR_IN_IFRAME = ".interaction-cloze-selectable-wrapper"
DROPDOWN_SELECT_TAG_IN_IFRAME = "select"


def connect_to_running_brave(port: int, driver_path: Optional[str] = None) -> Optional[RemoteWebDriver]:
    """
    Connects to a running instance of Brave browser started with remote debugging.

    Args:
        port: The remote debugging port Brave was started with.
        driver_path: Optional path to the ChromeDriver executable.

    Returns:
        A Selenium WebDriver instance if connection is successful, None otherwise.
    """
    print(f"Connecting to Brave (port {port})...")

    # Auto-install ChromeDriver if not provided
    if driver_path is None:
        print("ChromeDriver path not provided, attempting auto-installation...")
        driver_path = get_or_install_chromedriver()
        if not driver_path:
            print("❌ Failed to get ChromeDriver, falling back to system PATH")

    chrome_options = ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    service = None
    if driver_path and os.path.exists(driver_path):
        try:
            service = ChromeService(executable_path=driver_path)
            print(f"Using ChromeDriver from: {driver_path}")
        except Exception as e:
            print(f"ChromeService Error: {e}")
            print("Falling back to system PATH for ChromeDriver...")
            driver_path = None
    elif driver_path:
        print(f"Warning: Chromedriver path '{driver_path}' does not exist.")
        print("Falling back to system PATH for ChromeDriver...")
        driver_path = None

    if driver_path is None:
        print("Using ChromeDriver from system PATH...")

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options) if service else webdriver.Chrome(options=chrome_options)
        driver.set_script_timeout(10)
        driver.set_page_load_timeout(15)
        print("Connected to Brave.")
        return driver
    except WebDriverException as e:
        print(f"WebDriverException during Brave Connection: {e}")
        if "cannot find Chrome binary" in str(e).lower():
            print("Ensure Brave browser is installed and its location is in your system's PATH.")
        elif "unable to discover open pages" in str(e).lower() or "cannot connect" in str(e).lower():
            print(f"Ensure Brave is running with --remote-debugging-port={port} and has at least one active tab.")
            print("Example Brave launch command: brave.exe --remote-debugging-port=9222")
        return None
    except Exception as e:
        print(f"Generic Brave Connection Failed: {e}")
        return None


def find_and_switch_to_tab(driver: RemoteWebDriver, url_contains: str, title_contains: str) -> bool:
    """Finds and switches to a browser tab based on URL or title."""
    print(f"Looking for tab URL containing: '{url_contains}' or title containing: '{title_contains}'")
    original_handle: Optional[str] = None
    try:
        if driver.window_handles:
            original_handle = driver.current_window_handle
    except Exception:
        pass

    all_handles = driver.window_handles
    if not all_handles:
        print("No tabs open in the browser.")
        return False

    matched_tabs = []
    for handle in all_handles:
        try:
            driver.switch_to.window(handle)
            current_url = driver.current_url
            current_title = driver.title
            if (url_contains and url_contains.lower() in current_url.lower()) or \
               (title_contains and title_contains.lower() in current_title.lower()):
                matched_tabs.append({"handle": handle, "url": current_url, "title": current_title})
        except (NoSuchWindowException, WebDriverException):
            continue
        except Exception:
            continue

    if not matched_tabs:
        print("No matching tab found based on criteria.")
        if original_handle:
            try:
                driver.switch_to.window(original_handle)
            except Exception:
                pass
        return False

    target_tab_info = matched_tabs[0]
    print(f"Switching to tab: {target_tab_info['url']}")
    try:
        driver.switch_to.window(target_tab_info['handle'])
        time.sleep(0.05)
        WebDriverWait(driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        return True
    except Exception as e:
        print(f"Failed to switch to specific tab {target_tab_info['handle']}: {e}")
        if original_handle:
            try:
                driver.switch_to.window(original_handle)
            except Exception:
                pass
        return False


def get_element_with_wait(driver_or_element_context: Any, by_strategy: str, value: str,
                          timeout: int = 10, check_visible: bool = True) -> Optional[Any]:
    """Waits for an element to be present and optionally visible."""
    element: Optional[Any] = None
    try:
        wait = WebDriverWait(driver_or_element_context, timeout)
        element = wait.until(EC.presence_of_element_located((by_strategy, value)))

        if check_visible and element:
            current_driver = None
            if isinstance(driver_or_element_context, RemoteWebDriver):
                current_driver = driver_or_element_context
            elif hasattr(driver_or_element_context, 'parent') and isinstance(driver_or_element_context.parent, RemoteWebDriver):
                current_driver = driver_or_element_context.parent
            elif hasattr(element, 'parent') and isinstance(element.parent, RemoteWebDriver):
                current_driver = element.parent

            if current_driver and hasattr(current_driver, 'execute_script'):
                try:
                    current_driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
                    time.sleep(0.05)
                except Exception:
                    pass

            has_size = False
            size_check_duration = timeout * 0.20
            size_wait_end_time = time.time() + size_check_duration

            while time.time() < size_wait_end_time:
                try:
                    if not element.parent:
                        return None
                    current_size = element.size
                    if current_size['height'] > 0 and current_size['width'] > 0:
                        has_size = True
                        break
                    time.sleep(0.05)
                except StaleElementReferenceException:
                    try:
                        element = WebDriverWait(driver_or_element_context, 1).until(EC.presence_of_element_located((by_strategy, value)))
                    except TimeoutException:
                        return None
                except Exception:
                    break

            if not has_size:
                return None

            if element.is_displayed():
                return element
            else:
                visibility_timeout = max(1, int(timeout * 0.33) - int(size_check_duration))
                if visibility_timeout > 0 and current_driver:
                    try:
                        wait_visible = WebDriverWait(current_driver, visibility_timeout)
                        visible_element = wait_visible.until(EC.visibility_of(element))
                        return visible_element
                    except TimeoutException:
                        pass
                return None
        elif not element and check_visible:
            return None
        else:
            return element

    except TimeoutException:
        pass
    except Exception as e:
        print(f"Error finding element '{value}' by {by_strategy}: {e}")
    return None


def extract_dropdown_options_from_current_context(driver_or_element_context: Any) -> List[Dict[str, Any]]:
    """Extracts options from <select> elements within the current context."""
    dropdowns_data = []
    if not driver_or_element_context:
        return dropdowns_data

    select_elements: List[Any] = []
    try:
        if not hasattr(driver_or_element_context, 'find_elements'):
            return dropdowns_data

        # Try specific wrapper first
        wrappers = driver_or_element_context.find_elements(By.CSS_SELECTOR, DROPDOWN_PARENT_SELECTOR_IN_IFRAME)
        if wrappers:
            for wrapper in wrappers:
                try:
                    if wrapper.is_displayed():
                        sels = wrapper.find_elements(By.TAG_NAME, DROPDOWN_SELECT_TAG_IN_IFRAME)
                        select_elements.extend(sels)
                except StaleElementReferenceException:
                    continue

        if not select_elements:
            select_elements = driver_or_element_context.find_elements(By.TAG_NAME, DROPDOWN_SELECT_TAG_IN_IFRAME)

        if not select_elements:
            return []

        for i, select_el in enumerate(select_elements):
            try:
                if not select_el.is_displayed():
                    continue

                dd_id = select_el.get_attribute("id") or \
                        select_el.get_attribute("name") or \
                        f"dd_ctx_{i+1}"

                current_dd_data = {"id": dd_id, "options": []}
                opt_els = select_el.find_elements(By.TAG_NAME, "option")

                if not opt_els:
                    continue

                for opt in opt_els:
                    text = opt.text.strip()
                    value = opt.get_attribute("value")

                    is_placeholder = not text or \
                                     value == "-1" or \
                                     text.lower().startswith(("select", "choose", "please select"))

                    if not is_placeholder:
                        current_dd_data["options"].append({
                            "text": text if text else value,
                            "value": value if value else text
                        })

                if current_dd_data["options"]:
                    dropdowns_data.append(current_dd_data)
            except StaleElementReferenceException:
                continue
            except Exception as e_process_select:
                print(f"  Error processing select element {i+1}: {e_process_select}")
    except Exception as e:
        print(f"Overall error in extract_dropdown_options_from_current_context: {e}")

    return dropdowns_data


def capture_iframe_content_directly(driver: RemoteWebDriver, output_filename: str) -> Optional[str]:
    """Captures the full content of the currently active iframe using CDP."""
    emulation_active = False
    try:
        iframe_body = get_element_with_wait(driver, By.TAG_NAME, "body", timeout=2, check_visible=True)
        if not iframe_body:
            print("ERROR: iFrame body not found or not visible. Cannot capture.")
            return None

        scroll_w = driver.execute_script(
            "return Math.max( document.body.scrollWidth, document.documentElement.scrollWidth, document.body.offsetWidth, document.documentElement.offsetWidth, document.body.clientWidth, document.documentElement.clientWidth );"
        )
        scroll_h = driver.execute_script(
            "return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight );"
        )

        if not (isinstance(scroll_w, (int, float)) and scroll_w > 0 and isinstance(scroll_h, (int, float)) and scroll_h > 0):
            print(f"ERROR: iFrame content has invalid dimensions (W:{scroll_w}, H:{scroll_h}).")
            return None

        emulated_width = int(scroll_w / DEVICE_SCALE_FACTOR)
        emulated_height = int(scroll_h / DEVICE_SCALE_FACTOR)

        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': emulated_width,
            'height': emulated_height,
            'deviceScaleFactor': DEVICE_SCALE_FACTOR,
            'mobile': False
        })
        emulation_active = True
        time.sleep(0.1)

        screenshot_config = {
            'format': 'png',
            'captureBeyondViewport': True,
            'clip': {
                'x': 0,
                'y': 0,
                'width': scroll_w,
                'height': scroll_h,
                'scale': DEVICE_SCALE_FACTOR
            }
        }
        cdp_data = driver.execute_cdp_cmd('Page.captureScreenshot', screenshot_config)

        with open(output_filename, 'wb') as f:
            f.write(base64.b64decode(cdp_data['data']))

        img = Image.open(output_filename)
        if img.size[0] == 0 or img.size[1] == 0:
            print("ERROR: Saved iframe screenshot has zero dimensions.")
            os.remove(output_filename)
            return None
        return os.path.abspath(output_filename)

    except Exception as e:
        print(f"Error in capture_iframe_content_directly: {e}")
        traceback.print_exc()
        return None
    finally:
        if emulation_active:
            try:
                driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})
            except Exception:
                pass


def capture_main_container_fallback(driver: RemoteWebDriver, main_container_element: Any, output_filename: str) -> Optional[str]:
    """Fallback to capture a specific main container element."""
    emulation_active = False
    temp_fallback_ss = "temp_fallback_fullpage.png"

    try:
        location = main_container_element.location
        size = main_container_element.size

        if not (size and location and size.get('width', 0) > 0 and size.get('height', 0) > 0):
            print("Fallback Error: Main container element has no size or location.")
            return None

        page_actual_width = driver.execute_script("return Math.max( document.body.scrollWidth, document.documentElement.scrollWidth, document.body.offsetWidth, document.documentElement.offsetWidth, document.body.clientWidth, document.documentElement.clientWidth );")
        page_actual_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight );")

        em_w = int(max(page_actual_width, location['x'] + size['width'] + VIEWPORT_EMULATION_PADDING) / DEVICE_SCALE_FACTOR)
        em_h = int(max(page_actual_height, location['y'] + size['height'] + VIEWPORT_EMULATION_PADDING) / DEVICE_SCALE_FACTOR)

        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': em_w,
            'height': em_h,
            'deviceScaleFactor': DEVICE_SCALE_FACTOR,
            'mobile': False
        })
        emulation_active = True
        time.sleep(0.1)

        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", main_container_element)
            time.sleep(0.05)
        except Exception:
            pass

        cdp_data = driver.execute_cdp_cmd('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True})

        with open(temp_fallback_ss, 'wb') as f:
            f.write(base64.b64decode(cdp_data['data']))

        full_img = Image.open(temp_fallback_ss)
        page_ss_w, page_ss_h = full_img.size

        crop_x = location['x'] * DEVICE_SCALE_FACTOR
        crop_y = location['y'] * DEVICE_SCALE_FACTOR
        crop_w = size['width'] * DEVICE_SCALE_FACTOR
        crop_h = size['height'] * DEVICE_SCALE_FACTOR

        final_left = int(max(0, crop_x))
        final_upper = int(max(0, crop_y))
        final_right = int(min(page_ss_w, crop_x + crop_w))
        final_lower = int(min(page_ss_h, crop_y + crop_h))

        if final_right <= final_left or final_lower <= final_upper:
            print("Fallback crop invalid.")
            if os.path.exists(temp_fallback_ss):
                os.remove(temp_fallback_ss)
            return None

        cropped_img = full_img.crop((final_left, final_upper, final_right, final_lower))
        cropped_img.save(output_filename)

        if os.path.exists(temp_fallback_ss):
            os.remove(temp_fallback_ss)

        return os.path.abspath(output_filename)

    except Exception as e:
        print(f"Error in fallback screenshot: {e}")
        if os.path.exists(temp_fallback_ss):
            try:
                os.remove(temp_fallback_ss)
            except:
                pass
        return None
    finally:
        if emulation_active:
            try:
                driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})
            except Exception:
                pass


def capture_content_area_data(driver: RemoteWebDriver, main_container_locator_strategy: str,
                              main_container_locator_value: str, iframe_id_to_target: str,
                              output_filename: str) -> Dict[str, Any]:
    """Captures screenshot and dropdown data."""
    screenshot_path: Optional[str] = None
    dropdowns_data: List[Dict[str, Any]] = []
    error_message: Optional[str] = None
    final_status_message: str = "Task initiated."

    print(f"Attempt 1: Looking for main container '{main_container_locator_value}'.")
    main_container = get_element_with_wait(driver, main_container_locator_strategy, main_container_locator_value, timeout=2, check_visible=True)

    if main_container:
        final_status_message = f"Found main container '{main_container_locator_value}'."
        print(final_status_message)

        print(f"  Checking for iframe '{iframe_id_to_target}' within container.")
        iframe_in_container = get_element_with_wait(main_container, By.ID, iframe_id_to_target, timeout=2, check_visible=False)

        if iframe_in_container:
            final_status_message += f" Found iframe '{iframe_id_to_target}' inside."
            print(f"  Found iframe within main container. Processing its content.")
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", iframe_in_container)
                time.sleep(0.05)
                WebDriverWait(driver, 2).until(EC.frame_to_be_available_and_switch_to_it(iframe_in_container))
                print("  Switched to iframe context.")
                screenshot_path = capture_iframe_content_directly(driver, output_filename)
                if screenshot_path:
                    final_status_message += " Screenshot of inner iframe successful."
                    iframe_doc_body = get_element_with_wait(driver, By.TAG_NAME, "body", timeout=2, check_visible=True)
                    if iframe_doc_body:
                        dropdowns_data = extract_dropdown_options_from_current_context(iframe_doc_body)
                else:
                    error_message = f"Failed to capture screenshot of iframe '{iframe_id_to_target}'."
                    final_status_message += f" {error_message}"
                    print(f"  {error_message}")
            except Exception as e_iframe_proc:
                error_message = f"Error processing iframe: {e_iframe_proc}"
                final_status_message += f" Error: {error_message}"
                print(f"  {error_message}")
            finally:
                try:
                    driver.switch_to.default_content()
                except WebDriverException:
                    pass

        if not screenshot_path:
            if not iframe_in_container:
                final_status_message += " Inner iframe not found."
            else:
                final_status_message += " Inner iframe screenshot failed."
            print(f"  {final_status_message} Attempting to screenshot main container.")

            screenshot_path = capture_main_container_fallback(driver, main_container, output_filename)
            if screenshot_path:
                final_status_message += " Screenshot of main container successful."
                if not dropdowns_data:
                    dropdowns_data = extract_dropdown_options_from_current_context(main_container)
            else:
                emsg = f"Fallback screenshot of main container also failed."
                error_message = (error_message + ". " + emsg) if error_message else emsg
                final_status_message += f" Error: {emsg}"
                print(f"  {emsg}")

    else:
        final_status_message = f"Main container '{main_container_locator_value}' not found."
        print(final_status_message)
        print(f"Attempt 2: Looking for global iframe '{iframe_id_to_target}'.")
        global_iframe = get_element_with_wait(driver, By.ID, iframe_id_to_target, timeout=2, check_visible=False)

        if global_iframe:
            final_status_message += f" Found global iframe '{iframe_id_to_target}'."
            print(f"  Found global iframe. Processing its content.")
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", global_iframe)
                time.sleep(0.05)
                WebDriverWait(driver, 2).until(EC.frame_to_be_available_and_switch_to_it(global_iframe))
                print("  Switched to global iframe context.")
                screenshot_path = capture_iframe_content_directly(driver, output_filename)
                if screenshot_path:
                    final_status_message += " Screenshot of global iframe successful."
                    iframe_doc_body = get_element_with_wait(driver, By.TAG_NAME, "body", timeout=2, check_visible=True)
                    if iframe_doc_body:
                        dropdowns_data = extract_dropdown_options_from_current_context(iframe_doc_body)
                else:
                    error_message = f"Failed to capture screenshot of global iframe."
                    final_status_message += f" {error_message}"
                    print(f"  {error_message}")
            except Exception as e_global_iframe_proc:
                error_message = f"Error processing global iframe: {e_global_iframe_proc}"
                final_status_message += f" Error: {error_message}"
                print(f"  {error_message}")
            finally:
                try:
                    driver.switch_to.default_content()
                except WebDriverException:
                    pass
        else:
            final_status_message += f" Global iframe also not found."
            error_message = f"Neither main container nor global iframe were found."
            print(f"  {final_status_message}")

    if not screenshot_path and not error_message:
        error_message = "Screenshot capture failed for unknown reason."
        final_status_message += " Error: Unknown failure."
    elif screenshot_path:
        error_message = None

    print(f"Capture task final summary: {final_status_message}")
    return {"screenshot_path": screenshot_path, "dropdowns_data": dropdowns_data, "error": error_message}


def run_brave_screenshot_task() -> Dict[str, Any]:
    """
    Main task to connect to Brave, find the target tab, and capture content.

    Returns:
        A dictionary with 'screenshot_path', 'dropdowns_data', and 'error'.
    """
    print(f"Starting screenshot task at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    driver = connect_to_running_brave(DEBUGGING_PORT)

    if not driver:
        return {"screenshot_path": None, "dropdowns_data": [], "error": "Failed to connect to Brave."}

    capture_data: Dict[str, Any] = {"screenshot_path": None, "dropdowns_data": [], "error": "Task did not complete."}
    try:
        if not driver.window_handles:
            print("No tabs open after connection.")
            return {"screenshot_path": None, "dropdowns_data": [], "error": "No tabs open in Brave."}

        switched_to_target_tab = False
        if not (TARGET_TAB_URL_CONTAINS or TARGET_TAB_TITLE_CONTAINS):
            print(f"No tab target criteria. Using current tab: {driver.current_url}")
            switched_to_target_tab = True
        elif find_and_switch_to_tab(driver, TARGET_TAB_URL_CONTAINS, TARGET_TAB_TITLE_CONTAINS):
            current_url = driver.current_url
            if TARGET_TAB_URL_CONTAINS and TARGET_TAB_URL_CONTAINS.lower() not in current_url.lower():
                error_msg = f"ERROR: Tab validation failed. Current tab '{current_url}' does not match target."
                print(error_msg)
                capture_data["error"] = error_msg
                return capture_data
            switched_to_target_tab = True
        else:
            current_url_after_fail = driver.current_url
            error_msg = f"ERROR: No tab matching '{TARGET_TAB_URL_CONTAINS}' found. Please navigate to an Edmentum page."
            print(error_msg)
            capture_data["error"] = error_msg
            return capture_data

        if not switched_to_target_tab:
            capture_data["error"] = "Failed to identify a valid tab."
            return capture_data

        print(f"Operating on tab: {driver.current_url}")
        time.sleep(0.05)

        capture_data = capture_content_area_data(
            driver,
            MAIN_CONTAINER_LOCATOR_STRATEGY,
            MAIN_CONTAINER_LOCATOR_VALUE,
            IFRAME_ID,
            SCREENSHOT_FILENAME
        )

        if capture_data.get("screenshot_path"):
            print(f"\n--- Task Completed --- Screenshot: {capture_data['screenshot_path']}")
            if capture_data.get("dropdowns_data"):
                print(f"   Extracted {len(capture_data['dropdowns_data'])} dropdown(s).")
        else:
            err_msg = capture_data.get("error", "Could not capture screenshot.")
            print(f"\n--- Task Failed: {err_msg} ---")
            capture_data["error"] = err_msg
            capture_data["screenshot_path"] = None
            capture_data.setdefault("dropdowns_data", [])

    except WebDriverException as e:
        err_msg = f"WebDriver error: {e}"
        print(err_msg)
        capture_data = {"screenshot_path": None, "dropdowns_data": [], "error": err_msg}
    except Exception as e:
        err_msg = f"Unexpected error: {e}"
        print(err_msg)
        traceback.print_exc()
        capture_data = {"screenshot_path": None, "dropdowns_data": [], "error": err_msg}
    finally:
        print("Script finished. Leaving Brave open.")

    return capture_data


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # ChromeDriver auto-installation
    'get_brave_version',
    'get_matching_chromedriver_url',
    'download_and_install_chromedriver',
    'verify_chromedriver',
    'get_or_install_chromedriver',

    # Screenshot capture
    'connect_to_running_brave',
    'find_and_switch_to_tab',
    'capture_content_area_data',
    'run_brave_screenshot_task',
]
