import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException, NoSuchWindowException
import time
import os
from typing import Optional, List, Dict, Any
from PIL import Image
import base64
import traceback

# --- Configuration ---
DEBUGGING_PORT = 9222
# ChromeDriver path - will auto-detect if None or file doesn't exist
CHROMEDRIVER_PATH = None  # Set to None to use system PATH, or specify full path to chromedriver.exe
TARGET_TAB_URL_CONTAINS = "edmentum.com"
TARGET_TAB_TITLE_CONTAINS = "" # Optional: If title is more reliable
MAIN_CONTAINER_LOCATOR_STRATEGY = By.CLASS_NAME
MAIN_CONTAINER_LOCATOR_VALUE = "content-wrapper"
IFRAME_ID = "content-iframe" # This is the ID of the iframe, whether nested or global

SCREENSHOT_FILENAME = "final_content_shot.png" # Name for the screenshot file

VIEWPORT_EMULATION_PADDING = 20 # Padding for viewport emulation
DEVICE_SCALE_FACTOR = 1.0 # Device scale factor for CDP screenshots

DROPDOWN_PARENT_SELECTOR_IN_IFRAME = ".interaction-cloze-selectable-wrapper" # CSS selector for dropdown parent
DROPDOWN_SELECT_TAG_IN_IFRAME = "select" # Tag name for select element

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
    chrome_options = ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    # chrome_options.add_argument("--headless") # Uncomment if you want to run headless, though not typical for debugging connection
    # chrome_options.add_argument("--disable-gpu") # Often used with headless

    service = None
    if driver_path and os.path.exists(driver_path):
        try:
            service = ChromeService(executable_path=driver_path)
            print(f"Using ChromeDriver from: {driver_path}")
        except Exception as e:
            print(f"ChromeService Error: {e}")
            print("Falling back to system PATH for ChromeDriver...")
            driver_path = None  # Fall back to PATH
    elif driver_path:  # driver_path provided but doesn't exist
        print(f"Warning: Chromedriver path '{driver_path}' does not exist.")
        print("Falling back to system PATH for ChromeDriver...")
        driver_path = None  # Fall back to PATH

    # If driver_path is None, Selenium will try to find chromedriver in PATH
    if driver_path is None:
        print("Using ChromeDriver from system PATH...")

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options) if service else webdriver.Chrome(options=chrome_options)
        driver.set_script_timeout(10) # Optimized for fast captures
        driver.set_page_load_timeout(15) # Optimized for fast captures
        print("Connected to Brave.")
        return driver
    except WebDriverException as e:
        print(f"WebDriverException during Brave Connection: {e}")
        if "cannot find Chrome binary" in str(e).lower():
            print("Ensure Brave browser is installed and its location is in your system's PATH, or specify Brave binary location in options.")
        elif "unable to discover open pages" in str(e).lower() or "cannot connect" in str(e).lower():
            print(f"Ensure Brave is running with --remote-debugging-port={port} and has at least one active tab.")
            print("Example Brave launch command: brave.exe --remote-debugging-port=9222")
        return None
    except Exception as e:
        print(f"Generic Brave Connection Failed: {e}")
        return None

def find_and_switch_to_tab(driver: RemoteWebDriver, url_contains: str, title_contains: str) -> bool:
    """
    Finds and switches to a browser tab based on URL or title.
    Args:
        driver: The Selenium WebDriver instance.
        url_contains: A substring to match in the tab's URL (case-insensitive).
        title_contains: A substring to match in the tab's title (case-insensitive).
    Returns:
        True if a matching tab was found and switched to, False otherwise.
    """
    print(f"Looking for tab URL containing: '{url_contains}' or title containing: '{title_contains}'")
    original_handle: Optional[str] = None
    try:
        if driver.window_handles: # Check if there are any handles
            original_handle = driver.current_window_handle
    except Exception: # Catch if current_window_handle itself fails (e.g., browser closed)
        pass

    all_handles = driver.window_handles
    if not all_handles:
        print("No tabs open in the browser.")
        return False

    matched_tabs = []
    for handle in all_handles:
        try:
            driver.switch_to.window(handle)
            # Context switch is immediate, no sleep needed
            current_url = driver.current_url
            current_title = driver.title
            # print(f" Checking Handle: {handle}, URL: {current_url}, Title: {current_title}") # Debug
            if (url_contains and url_contains.lower() in current_url.lower()) or \
               (title_contains and title_contains.lower() in current_title.lower()):
                matched_tabs.append({"handle": handle, "url": current_url, "title": current_title})
        except (NoSuchWindowException, WebDriverException):
            # print(f"  Window {handle} closed or inaccessible during search.") # Debug
            continue # Tab might have closed during iteration
        except Exception as e_switch:
            # print(f"  Error switching to or getting info from window {handle}: {e_switch}") # Debug
            continue


    if not matched_tabs:
        print("No matching tab found based on criteria.")
        if original_handle: # Switch back if we had an original handle and didn't find a match
            try:
                driver.switch_to.window(original_handle)
            except Exception:
                pass # Original handle might also be gone
        return False

    # Prioritize more specific matches or the first one found
    target_tab_info = matched_tabs[0] # Taking the first match
    print(f"Switching to tab: {target_tab_info['url']}")
    try:
        driver.switch_to.window(target_tab_info['handle'])
        time.sleep(0.05) # Allow a bit more time for the switch to fully take effect
        # Wait for the page to be in a ready state
        WebDriverWait(driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        return True
    except Exception as e:
        print(f"Failed to switch to specific tab {target_tab_info['handle']} or wait for page load: {e}")
        if original_handle: # Attempt to switch back to original if final switch failed
            try:
                driver.switch_to.window(original_handle)
            except Exception:
                pass
        return False

def get_element_with_wait(driver_or_element_context: Any, by_strategy: str, value: str, timeout: int = 10, check_visible: bool = True) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Waits for an element to be present and optionally visible and have size.
    Args:
        driver_or_element_context: WebDriver instance or a WebElement to search within.
        by_strategy: Selenium By strategy (e.g., By.ID, By.CLASS_NAME).
        value: The value of the locator.
        timeout: Maximum time to wait for presence.
        check_visible: If True, also checks for visibility and size.
    Returns:
        The WebElement if found and conditions met, None otherwise.
    """
    # print(f"Attempting to find element by {by_strategy}='{value}' (presence timeout: {timeout}s)")
    element: Optional[webdriver.remote.webelement.WebElement] = None
    try:
        wait = WebDriverWait(driver_or_element_context, timeout)
        element = wait.until(EC.presence_of_element_located((by_strategy, value)))
        # print(f"Element found by {by_strategy}='{value}' (present).")

        if check_visible and element: # Proceed only if element is not None
            # print(f"Checking visibility for element {by_strategy}='{value}'...")
            # Determine the current driver context for executing scripts
            current_driver = None
            if isinstance(driver_or_element_context, RemoteWebDriver):
                current_driver = driver_or_element_context
            elif hasattr(driver_or_element_context, 'parent') and isinstance(driver_or_element_context.parent, RemoteWebDriver):
                current_driver = driver_or_element_context.parent
            elif hasattr(element, 'parent') and isinstance(element.parent, RemoteWebDriver) : # type: ignore
                 current_driver = element.parent # type: ignore

            if current_driver and hasattr(current_driver, 'execute_script'):
                try:
                    current_driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
                    # print("Scrolled element into view (center).")
                    time.sleep(0.05) # Optimized: minimal sleep after scroll
                except Exception as scroll_e:
                    print(f"Note: Error trying to scroll element into view: {scroll_e}")
            # else: print("Warning: Could not determine driver for scrolling element into view from context.")


            has_size = False
            size_check_duration = timeout * 0.20 # Optimized: only use 20% of timeout for size checking
            size_wait_end_time = time.time() + size_check_duration
            # print(f"Waiting for element to acquire size (up to {size_check_duration:.2f}s)...")

            while time.time() < size_wait_end_time:
                try:
                    if not element.parent: # Check if element became detached
                        # print(f"Element {by_strategy}='{value}' became detached from DOM during size check.")
                        return None
                    current_size = element.size
                    if current_size['height'] > 0 and current_size['width'] > 0:
                        # print(f"Element {by_strategy}='{value}' now has size: {current_size}.")
                        has_size = True
                        break
                    time.sleep(0.05) # Optimized: faster polling for quicker detection
                except StaleElementReferenceException:
                    # print(f"StaleElementReferenceException while waiting for size for {by_strategy}='{value}'. Re-finding...")
                    try: # Short re-find attempt
                        element = WebDriverWait(driver_or_element_context, 1).until(EC.presence_of_element_located((by_strategy, value))) # type: ignore
                        # print("Re-found element.")
                    except TimeoutException:
                        # print(f"Could not re-find element {by_strategy}='{value}' after stale reference.")
                        return None 
                except Exception as e_size_check:
                    # print(f"Exception during size check for {by_strategy}='{value}': {e_size_check}")
                    break 
            
            if not has_size:
                # final_size = "N/A"
                # try: final_size = element.size if element and element.parent else "Detached or N/A" # type: ignore
                # except: pass
                # print(f"Element {by_strategy}='{value}' did not acquire size. Final checked size: {final_size}")
                return None # Did not acquire size

            if element.is_displayed():
                # print(f"Element {by_strategy}='{value}' is_displayed() returned True (after size check).")
                return element
            else:
                # print(f"Element {by_strategy}='{value}' has size but is_displayed() returned False.")
                # Attempting EC.visibility_of as a last resort if is_displayed is false even with size
                visibility_timeout = max(1, int(timeout * 0.33) - int(size_check_duration)) 
                if visibility_timeout > 0 and current_driver: # Ensure current_driver is available
                    # print(f"Attempting explicit EC.visibility_of(element) with timeout {visibility_timeout}s...")
                    try:
                        wait_visible = WebDriverWait(current_driver, visibility_timeout) # Use current_driver here
                        visible_element = wait_visible.until(EC.visibility_of(element))
                        # print(f"Element {by_strategy}='{value}' confirmed visible by EC.visibility_of.")
                        return visible_element
                    except TimeoutException:
                        # print(f"Timeout: Element {by_strategy}='{value}' not visible via EC.visibility_of after size check.")
                        pass # Fall through to return None
                return None # Not displayed
        elif not element and check_visible: # Element not found by presence, and visibility check was requested
             return None
        else: # Element found by presence, and check_visible is False (or element was None initially)
            return element

    except TimeoutException:
        # print(f"Timeout: Element not present within {timeout}s (presence_of_element_located): {by_strategy}='{value}'")
        pass
    except Exception as e:
        print(f"Error finding element '{value}' by {by_strategy}: {e}")
        traceback.print_exc()
    return None

def extract_dropdown_options_from_current_context(driver_or_element_context: Any) -> List[Dict[str, Any]]:
    """
    Extracts options from <select> elements within the current context (driver or a specific element).
    Args:
        driver_or_element_context: WebDriver or WebElement to search within.
    Returns:
        A list of dictionaries, each representing a dropdown with its options.
    """
    dropdowns_data = []
    if not driver_or_element_context:
        print("Context for dropdown extraction is None.")
        return dropdowns_data

    select_elements: List[webdriver.remote.webelement.WebElement] = []
    try:
        if not hasattr(driver_or_element_context, 'find_elements'):
            print("Context invalid for find_elements for dropdown extraction.")
            return dropdowns_data

        # Try specific wrapper first
        wrappers = driver_or_element_context.find_elements(By.CSS_SELECTOR, DROPDOWN_PARENT_SELECTOR_IN_IFRAME)
        if wrappers:
            # print(f"Found {len(wrappers)} potential dropdown wrappers using '{DROPDOWN_PARENT_SELECTOR_IN_IFRAME}'.")
            for idx, wrapper in enumerate(wrappers):
                try:
                    if wrapper.is_displayed(): # Check if wrapper is visible
                        sels = wrapper.find_elements(By.TAG_NAME, DROPDOWN_SELECT_TAG_IN_IFRAME)
                        select_elements.extend(sels)
                        # if sels: print(f"  Found {len(sels)} select(s) in visible wrapper {idx+1}.")
                except StaleElementReferenceException:
                    # print(f"Wrapper {idx+1} became stale during dropdown check.")
                    continue
        
        # If no selects found in wrappers, or no wrappers, search for all select tags in the context
        if not select_elements:
            # print(f"No selects in wrappers or no wrappers. Searching all '{DROPDOWN_SELECT_TAG_IN_IFRAME}' tags in context.")
            select_elements = driver_or_element_context.find_elements(By.TAG_NAME, DROPDOWN_SELECT_TAG_IN_IFRAME)

        if not select_elements:
            # print("No select elements found for dropdown extraction in the current context.")
            return []

        # print(f"Processing {len(select_elements)} select elements for dropdown options.")
        for i, select_el in enumerate(select_elements):
            try:
                if not select_el.is_displayed():
                    # print(f"  Select element {i+1} is not visible, skipping.")
                    continue

                # Generate a unique ID for the dropdown based on its attributes if possible, or index
                dd_id = select_el.get_attribute("id") or \
                        select_el.get_attribute("name") or \
                        f"dd_ctx_{i+1}" # Fallback ID

                current_dd_data = {"id": dd_id, "options": []}
                opt_els = select_el.find_elements(By.TAG_NAME, "option")

                if not opt_els:
                    # print(f"  Select {current_dd_data['id']} has no <option> tags.")
                    continue

                for opt in opt_els:
                    text = opt.text.strip()
                    value = opt.get_attribute("value")
                    
                    # Filter out placeholder-like options
                    is_placeholder = not text or \
                                     value == "-1" or \
                                     text.lower().startswith(("select", "choose", "please select"))
                    
                    if not is_placeholder:
                        current_dd_data["options"].append({
                            "text": text if text else value, # Use value if text is empty
                            "value": value if value else text  # Use text if value is empty
                        })
                
                if current_dd_data["options"]:
                    dropdowns_data.append(current_dd_data)
                    # print(f"  Extracted for {current_dd_data['id']}: {len(current_dd_data['options'])} options.")
            except StaleElementReferenceException:
                # print(f"  Select/option element {i+1} became stale during processing.")
                continue
            except Exception as e_process_select:
                print(f"  Error processing select element {i+1}: {e_process_select}")
    except Exception as e:
        print(f"Overall error in extract_dropdown_options_from_current_context: {e}")
        traceback.print_exc()
    
    return dropdowns_data

def capture_iframe_content_directly(driver: RemoteWebDriver, output_filename: str) -> Optional[str]:
    """
    Captures the full content of the currently active iframe using CDP.
    Args:
        driver: The Selenium WebDriver instance (must be switched to the iframe context).
        output_filename: The filename to save the screenshot to.
    Returns:
        The absolute path to the saved screenshot if successful, None otherwise.
    """
    emulation_active = False
    try:
        # Ensure we are in an iframe context and can access its body
        iframe_body = get_element_with_wait(driver, By.TAG_NAME, "body", timeout=2, check_visible=True)
        if not iframe_body:
            print("ERROR: iFrame body not found or not visible within current context. Cannot capture.")
            return None

        # Get the full scrollable dimensions of the iframe's content
        scroll_w = driver.execute_script(
            "return Math.max( document.body.scrollWidth, document.documentElement.scrollWidth, document.body.offsetWidth, document.documentElement.offsetWidth, document.body.clientWidth, document.documentElement.clientWidth );"
        )
        scroll_h = driver.execute_script(
            "return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight );"
        )

        if not (isinstance(scroll_w, (int, float)) and scroll_w > 0 and isinstance(scroll_h, (int, float)) and scroll_h > 0):
            print(f"ERROR: iFrame content has invalid or zero dimensions (W:{scroll_w}, H:{scroll_h}). Cannot capture.")
            return None
        
        # print(f"iFrame internal content scroll dimensions - W: {scroll_w}, H: {scroll_h}")

        # Emulate device metrics to capture the entire scrollable area
        # The viewport width/height for emulation should be based on the content's scroll dimensions
        # We use int() for pixel values required by CDP.
        emulated_width = int(scroll_w / DEVICE_SCALE_FACTOR)
        emulated_height = int(scroll_h / DEVICE_SCALE_FACTOR)

        # print(f"Emulating iframe viewport: Target CSS W={scroll_w}, H={scroll_h}, DeviceScaleFactor={DEVICE_SCALE_FACTOR}")
        # print(f"CDP Emulation.setDeviceMetricsOverride: width={emulated_width}, height={emulated_height}")

        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': emulated_width,
            'height': emulated_height,
            'deviceScaleFactor': DEVICE_SCALE_FACTOR,
            'mobile': False # Assuming desktop content
        })
        emulation_active = True
        time.sleep(0.1) # Optimized: reduced delay for layout reflow

        # print("Attempting iframe content screenshot via CDP Page.captureScreenshot...")
        # Define the clip for the screenshot to match the content dimensions
        screenshot_config = {
            'format': 'png',
            'captureBeyondViewport': True, # Important for full page
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
        # print(f"iFrame content screenshot saved to {output_filename}")

        # Verify image
        img = Image.open(output_filename)
        # print(f"Saved iframe image dimensions: {img.size}")
        if img.size[0] == 0 or img.size[1] == 0:
            print("ERROR: Saved iframe screenshot has zero dimensions. Deleting file.")
            os.remove(output_filename)
            return None
        return os.path.abspath(output_filename)

    except Exception as e:
        print(f"Error in capture_iframe_content_directly: {e}")
        traceback.print_exc()
        return None
    finally:
        if emulation_active:
            # print("Clearing iframe CDP emulation...");
            try:
                driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})
            except Exception as e_clear:
                # print(f"Note: Error clearing device metrics override: {e_clear}")
                pass

def capture_main_container_fallback(driver: RemoteWebDriver, main_container_element: webdriver.remote.webelement.WebElement, output_filename: str) -> Optional[str]:
    """
    Fallback to capture a specific main container element if iframe processing fails.
    Args:
        driver: The Selenium WebDriver instance.
        main_container_element: The WebElement of the main container.
        output_filename: The filename to save the screenshot to.
    Returns:
        The absolute path to the saved screenshot if successful, None otherwise.
    """
    # print(f"Fallback: Attempting to screenshot element: <{main_container_element.tag_name} class='{main_container_element.get_attribute('class')}'>")
    emulation_active = False
    temp_fallback_ss = "temp_fallback_fullpage.png" # For the intermediate full-page shot

    try:
        location = main_container_element.location
        size = main_container_element.size 

        if not (size and location and size.get('width', 0) > 0 and size.get('height', 0) > 0):
            print("Fallback Error: Main container element has no size or location.")
            return None

        # Get full page dimensions for emulation to ensure the element is within the captured area
        page_actual_width = driver.execute_script("return Math.max( document.body.scrollWidth, document.documentElement.scrollWidth, document.body.offsetWidth, document.documentElement.offsetWidth, document.body.clientWidth, document.documentElement.clientWidth );")
        page_actual_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.body.clientHeight, document.documentElement.clientHeight );")

        # Ensure emulated viewport is large enough to contain the element fully
        em_w = int(max(page_actual_width, location['x'] + size['width'] + VIEWPORT_EMULATION_PADDING) / DEVICE_SCALE_FACTOR)
        em_h = int(max(page_actual_height, location['y'] + size['height'] + VIEWPORT_EMULATION_PADDING) / DEVICE_SCALE_FACTOR)
        
        # print(f"Fallback emulation using page/generous dimensions: Emulated W={em_w}, H={em_h}")
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': em_w, 
            'height': em_h, 
            'deviceScaleFactor': DEVICE_SCALE_FACTOR, 
            'mobile': False
        })
        emulation_active = True
        time.sleep(0.1) # Optimized: reduced delay for layout reflow

        try: # Scroll the specific element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", main_container_element)
            # print("Scrolled main_container_element into view for fallback."); 
            time.sleep(0.05) # Optimized delay
        except Exception as e_scroll:
            print(f"Note: Could not scroll main_container_element into view during fallback: {e_scroll}")

        # print("Capturing full page screenshot via CDP for fallback cropping...")
        # Capture the entire emulated viewport
        cdp_data = driver.execute_cdp_cmd('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True})
        
        with open(temp_fallback_ss, 'wb') as f:
            f.write(base64.b64decode(cdp_data['data']))
        
        full_img = Image.open(temp_fallback_ss)
        page_ss_w, page_ss_h = full_img.size
        # print(f"Full page screenshot for fallback captured with dimensions: {page_ss_w}x{page_ss_h}")

        # Calculate crop box based on element's location and size relative to the full page screenshot
        # Location and size are in CSS pixels, scale them by deviceScaleFactor for image pixels
        crop_x = location['x'] * DEVICE_SCALE_FACTOR
        crop_y = location['y'] * DEVICE_SCALE_FACTOR
        crop_w = size['width'] * DEVICE_SCALE_FACTOR
        crop_h = size['height'] * DEVICE_SCALE_FACTOR
        
        # print(f"Fallback crop box calculation (scaled): x={crop_x}, y={crop_y}, w={crop_w}, h={crop_h}")

        final_left = int(max(0, crop_x))
        final_upper = int(max(0, crop_y))
        final_right = int(min(page_ss_w, crop_x + crop_w))
        final_lower = int(min(page_ss_h, crop_y + crop_h))

        if final_right <= final_left or final_lower <= final_upper:
            print(f"Fallback crop invalid. L={final_left}, U={final_upper}, R={final_right}, Lw={final_lower}. Full page image might not contain the element as expected.");
            if os.path.exists(temp_fallback_ss): os.remove(temp_fallback_ss)
            return None
            
        # print(f"Cropping fallback at (L,U,R,Lw): [{final_left}, {final_upper}, {final_right}, {final_lower}] from page screenshot size {page_ss_w}x{page_ss_h}")
        cropped_img = full_img.crop((final_left, final_upper, final_right, final_lower))
        cropped_img.save(output_filename)
        # print(f"Fallback screenshot saved: {output_filename} with dimensions {cropped_img.size}")
        
        if os.path.exists(temp_fallback_ss):
            os.remove(temp_fallback_ss)
        
        return os.path.abspath(output_filename)

    except Exception as e:
        print(f"Error in fallback screenshot: {e}")
        traceback.print_exc()
        if os.path.exists(temp_fallback_ss): # Cleanup temp file on error
            try: os.remove(temp_fallback_ss)
            except: pass
        return None
    finally:
        if emulation_active:
            try:
                driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})
                # print("Cleared device metrics override after fallback.")
            except Exception as e_clear:
                # print(f"Note: Error clearing device metrics override after fallback: {e_clear}")
                pass

def capture_content_area_data(driver: RemoteWebDriver, main_container_locator_strategy: str, main_container_locator_value: str, iframe_id_to_target: str, output_filename: str) -> Dict[str, Any]:
    """
    Captures screenshot and dropdown data, prioritizing main_container and its iframe,
    then falling back to a global iframe if main_container is not found.
    """
    screenshot_path: Optional[str] = None
    dropdowns_data: List[Dict[str, Any]] = []
    error_message: Optional[str] = None
    final_status_message: str = "Task initiated."

    # Attempt 1: Find main_container and process it (including its potential inner iframe)
    print(f"Attempt 1: Looking for main container '{main_container_locator_value}' using {main_container_locator_strategy}.")
    main_container = get_element_with_wait(driver, main_container_locator_strategy, main_container_locator_value, timeout=2, check_visible=True)

    if main_container:
        final_status_message = f"Found main container '{main_container_locator_value}'."
        print(final_status_message)
        
        # Check for iframe *within* the main_container
        print(f"  Checking for iframe '{iframe_id_to_target}' within '{main_container_locator_value}'.")
        iframe_in_container = get_element_with_wait(main_container, By.ID, iframe_id_to_target, timeout=2, check_visible=False)

        if iframe_in_container:
            final_status_message += f" Found iframe '{iframe_id_to_target}' inside."
            print(f"  Found iframe '{iframe_id_to_target}' within main container. Processing its content.")
            try:
                # Scroll the iframe element itself into view on the main page before switching
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", iframe_in_container)
                time.sleep(0.05) # Brief pause for scrolling
                WebDriverWait(driver, 2).until(EC.frame_to_be_available_and_switch_to_it(iframe_in_container))
                print("  Switched to iframe (in container) context successfully.")
                screenshot_path = capture_iframe_content_directly(driver, output_filename)
                if screenshot_path:
                    final_status_message += " Screenshot of inner iframe successful."
                    # print("  Screenshot of iframe (in container) content successful.")
                    iframe_doc_body = get_element_with_wait(driver, By.TAG_NAME, "body", timeout=2, check_visible=True)
                    if iframe_doc_body:
                        dropdowns_data = extract_dropdown_options_from_current_context(iframe_doc_body)
                        # if dropdowns_data: print(f"  Extracted {len(dropdowns_data)} dropdowns from inner iframe.")
                        # else: print("  No dropdowns in inner iframe body.")
                    # else: print("  Could not find body within inner iframe for dropdown extraction.")
                else:
                    error_message = f"Failed to capture screenshot of iframe '{iframe_id_to_target}' (in container)."
                    final_status_message += f" {error_message}"
                    print(f"  {error_message}")
            except Exception as e_iframe_proc:
                error_message = f"Error processing iframe '{iframe_id_to_target}' (in container): {e_iframe_proc}"
                final_status_message += f" Error: {error_message}"
                print(f"  {error_message}"); traceback.print_exc()
            finally:
                # print("  Switching back to default content from iframe (in container).")
                try: driver.switch_to.default_content()
                except WebDriverException: pass
        
        # If no screenshot yet (either inner iframe not found, or its screenshot failed), try main_container itself
        if not screenshot_path:
            if not iframe_in_container : final_status_message += " Inner iframe not found."
            else: final_status_message += " Inner iframe screenshot failed."
            print(f"  {final_status_message} Attempting to screenshot main container '{main_container_locator_value}'.")
            
            screenshot_path = capture_main_container_fallback(driver, main_container, output_filename)
            if screenshot_path:
                final_status_message += " Screenshot of main container successful."
                # print(f"  Fallback screenshot of main container '{main_container_locator_value}' successful.")
                if not dropdowns_data: # Only extract if not already done from an inner iframe
                    # print("  Attempting dropdown extraction from main container.")
                    dropdowns_data = extract_dropdown_options_from_current_context(main_container)
                    # if dropdowns_data: print(f"  Extracted {len(dropdowns_data)} dropdowns from main container.")
                    # else: print("  No dropdowns in main container.")
            else:
                emsg = f"Fallback screenshot of main container '{main_container_locator_value}' also failed."
                error_message = (error_message + ". " + emsg) if error_message else emsg
                final_status_message += f" Error: {emsg}"
                print(f"  {emsg}")

    else: # Main container was NOT found
        final_status_message = f"Main container '{main_container_locator_value}' not found."
        print(final_status_message)
        print(f"Attempt 2: Looking for global iframe '{iframe_id_to_target}'.")
        global_iframe = get_element_with_wait(driver, By.ID, iframe_id_to_target, timeout=2, check_visible=False)

        if global_iframe:
            final_status_message += f" Found global iframe '{iframe_id_to_target}'."
            print(f"  Found global iframe '{iframe_id_to_target}'. Processing its content.")
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", global_iframe)
                time.sleep(0.05)
                WebDriverWait(driver, 2).until(EC.frame_to_be_available_and_switch_to_it(global_iframe))
                print("  Switched to global iframe context successfully.")
                screenshot_path = capture_iframe_content_directly(driver, output_filename)
                if screenshot_path:
                    final_status_message += " Screenshot of global iframe successful."
                    # print("  Screenshot of global iframe content successful.")
                    iframe_doc_body = get_element_with_wait(driver, By.TAG_NAME, "body", timeout=2, check_visible=True)
                    if iframe_doc_body:
                        dropdowns_data = extract_dropdown_options_from_current_context(iframe_doc_body)
                        # if dropdowns_data: print(f"  Extracted {len(dropdowns_data)} dropdowns from global iframe.")
                        # else: print("  No dropdowns in global iframe body.")
                    # else: print("  Could not find body within global iframe for dropdown extraction.")
                else:
                    error_message = f"Failed to capture screenshot of global iframe '{iframe_id_to_target}'."
                    final_status_message += f" {error_message}"
                    print(f"  {error_message}")
            except Exception as e_global_iframe_proc:
                error_message = f"Error processing global iframe '{iframe_id_to_target}': {e_global_iframe_proc}"
                final_status_message += f" Error: {error_message}"
                print(f"  {error_message}"); traceback.print_exc()
            finally:
                # print("  Switching back to default content from global iframe.")
                try: driver.switch_to.default_content()
                except WebDriverException: pass
        else:
            final_status_message += f" Global iframe '{iframe_id_to_target}' also not found."
            error_message = f"Neither main container '{main_container_locator_value}' nor global iframe '{iframe_id_to_target}' were found or could be processed."
            print(f"  {final_status_message}")
            
    if not screenshot_path and not error_message: # Should not happen if logic is correct, but as a safeguard
        error_message = "Screenshot capture failed for an unknown reason after all attempts."
        final_status_message += " Error: Unknown screenshot failure."
    elif screenshot_path: # Clear error if screenshot was successful
        error_message = None 

    print(f"Capture task final summary: {final_status_message}")
    return {"screenshot_path": screenshot_path, "dropdowns_data": dropdowns_data, "error": error_message}


def run_brave_screenshot_task() -> Dict[str, Any]:
    """
    Main task to connect to Brave, find the target tab, and capture content.
    Returns:
        A dictionary with 'screenshot_path', 'dropdowns_data', and 'error'.
    """
    print(f"Starting script execution at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    driver = connect_to_running_brave(DEBUGGING_PORT, CHROMEDRIVER_PATH)
    
    if not driver:
        return {"screenshot_path": None, "dropdowns_data": [], "error": "Failed to connect to Brave."}

    capture_data: Dict[str, Any] = {"screenshot_path": None, "dropdowns_data": [], "error": "Task did not complete."}
    try:
        if not driver.window_handles: # Check immediately after connection
            print("No tabs open after successful connection to Brave.")
            return {"screenshot_path": None, "dropdowns_data": [], "error": "No tabs open in Brave."}

        switched_to_target_tab = False
        if not (TARGET_TAB_URL_CONTAINS or TARGET_TAB_TITLE_CONTAINS):
            print(f"No tab target criteria (URL/Title) defined. Using current active tab: {driver.current_url}")
            switched_to_target_tab = True # Assume current tab is the target
        elif find_and_switch_to_tab(driver, TARGET_TAB_URL_CONTAINS, TARGET_TAB_TITLE_CONTAINS):
            # Strict validation: Verify that the current URL actually contains the target string
            current_url = driver.current_url
            if TARGET_TAB_URL_CONTAINS and TARGET_TAB_URL_CONTAINS.lower() not in current_url.lower():
                error_msg = f"ERROR: Tab validation failed. Current tab '{current_url}' does not match target '{TARGET_TAB_URL_CONTAINS}'. Please open an Edmentum page before capturing."
                print(error_msg)
                capture_data["error"] = error_msg
                return capture_data
            switched_to_target_tab = True
        else:
            # STRICT MODE: Do NOT fall back to any other tab. Require exact match.
            current_url_after_fail_switch = driver.current_url
            error_msg = f"ERROR: No tab matching '{TARGET_TAB_URL_CONTAINS}' found. Current tab '{current_url_after_fail_switch}' is not a valid target. Please navigate to an Edmentum page and try again."
            print(error_msg)
            capture_data["error"] = error_msg
            return capture_data

        if not switched_to_target_tab: # Should be covered by above, but as a safeguard
            capture_data["error"] = "Failed to identify a valid tab to operate on."
            return capture_data
            
        print(f"Operating on tab: {driver.current_url}")
        time.sleep(0.05) # Optimized: minimal pause after tab switch

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
                print("   No dropdown data extracted.")
            # If there was an error message but a screenshot was still produced (e.g. minor issue), log it.
            if capture_data.get("error"): 
                print(f"   Note during capture: {capture_data['error']}")
        else:
            # Ensure error from capture_data is used, or provide a generic one.
            err_msg = capture_data.get("error", "Could not capture screenshot or extract data for unknown reasons.")
            print(f"\n--- Task Failed: {err_msg} ---")
            # Ensure capture_data is a dict and has the error set for return
            if not isinstance(capture_data, dict): capture_data = {}
            capture_data["error"] = err_msg
            capture_data["screenshot_path"] = None # Ensure it's None if failed
            capture_data.setdefault("dropdowns_data", [])


    except WebDriverException as e:
        err_msg = f"WebDriver error during task: {e}"
        print(err_msg)
        if "disconnected" in str(e).lower() or "target window already closed" in str(e).lower() or "no such window" in str(e).lower() :
            print("Browser or target tab may have been closed unexpectedly.")
        capture_data = {"screenshot_path": None, "dropdowns_data": [], "error": err_msg}
    except Exception as e:
        err_msg = f"Unexpected error during main task: {e}"
        print(err_msg)
        traceback.print_exc()
        capture_data = {"screenshot_path": None, "dropdowns_data": [], "error": err_msg}
    finally:
        # According to original logic: "Leaving Brave open."
        # If you wanted to close the driver:
        # if driver:
        #     driver.quit()
        #     print("WebDriver session closed.")
        print("Script finished. Leaving Brave open.")
    
    return capture_data

# if __name__ == "__main__":
#     result = run_brave_screenshot_task()
#     print("\n--- FINAL RESULT ---")
#     if result.get("screenshot_path"):
#         print(f"Screenshot: {result['screenshot_path']}")
#     if result.get("dropdowns_data"):
#         print(f"Dropdowns: {len(result['dropdowns_data'])}")
#         # for dd in result['dropdowns_data']: print(dd) # For detailed dropdown print
#     if result.get("error"):
#         print(f"Error: {result['error']}")
