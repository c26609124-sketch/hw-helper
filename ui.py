import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import threading
import sys
import os
import time
import json
import traceback
import tkinter
import re # Import regular expressions for parsing placeholders
import random # Added for replacing "None"
import subprocess # For launching Brave browser
import platform # For OS detection
from pathlib import Path # For icon directory path resolution
from tkinter import filedialog # For file selection dialog
from typing import Dict, List, Optional, Tuple, Union # Type hints for progressive parser

# --- OpenRouter API Integration ---
import requests
import base64
from datetime import datetime

# --- Enhanced Visual Display ---
try:
    from enhanced_answer_display import EnhancedAnswerPresenter, DragToImageRenderer
    from visual_element_detector import VisualElementDetector
    VISUAL_ENHANCEMENT_AVAILABLE = True
except ImportError as e:
    print(f"Note: Visual enhancement modules not available: {e}")
    VISUAL_ENHANCEMENT_AVAILABLE = False

# --- Progressive JSON Parser ---
try:
    from progressive_json_parser import ProgressiveJSONParser
    PROGRESSIVE_PARSER_AVAILABLE = True
except ImportError as e:
    print(f"Note: Progressive parser not available: {e}")
    PROGRESSIVE_PARSER_AVAILABLE = False

# --- Edmentum Question Renderer ---
try:
    from edmentum_components import EdmentumQuestionRenderer
    EDMENTUM_RENDERER_AVAILABLE = True
except ImportError as e:
    print(f"Note: Edmentum renderer not available: {e}")
    EDMENTUM_RENDERER_AVAILABLE = False

# --- Response Validator ---
try:
    from response_validator import validate_response
    RESPONSE_VALIDATOR_AVAILABLE = True
except ImportError as e:
    print(f"Note: Response validator not available: {e}")
    RESPONSE_VALIDATOR_AVAILABLE = False

# --- Auto Updater ---
try:
    from auto_updater import check_for_updates_silent, apply_update_silent
    AUTO_UPDATER_AVAILABLE = True
except ImportError as e:
    print(f"Note: Auto updater not available: {e}")
    AUTO_UPDATER_AVAILABLE = False

# --- Discord Error Reporting ---
DISCORD_ERROR_WEBHOOK = "https://discord.com/api/webhooks/1433581225443852358/zM7WtUo3N6FRigTtJfgmtzXpu5_giyrWrkbcz7nTej8QiJjNAQCfqlta8m5_eCabta3b"

# --- PIL Text Capability Check ---
try:
    from PIL import ImageDraw, ImageFont 
    PIL_TEXT_CAPABLE = True
except ImportError:
    PIL_TEXT_CAPABLE = False
    print("***********************************************************************************")
    print("WARNING: Could not import ImageDraw, ImageFont from PIL. Text on stub image may not work.")
    print("***********************************************************************************")


# --- Edmentum Styling Constants (for skeleton rendering) ---
EDMENTUM_SKELETON_STYLES = {
    'border_radius': 6,
    'margin_option': 8,
    'font_family': 'Arial',
    'font_size_option': 14,
}

def get_edmentum_color(key: str, dark_mode: bool = False) -> str:
    """Get Edmentum colors for skeleton rendering"""
    light_colors = {
        'bg_primary': '#FFFFFF',
        'gray_border': '#DEE2E6',
        'gray_light': '#E9ECEF',
        'green_correct': '#28A745',
        'green_light': '#D4EDDA',
        'gray_text': '#6C757D',
    }
    dark_colors = {
        'bg_primary': '#1E1E1E',
        'gray_border': '#404040',
        'gray_light': '#353535',
        'green_correct': '#4CAF50',
        'green_light': '#1a311a',
        'gray_text': '#B0B0B0',
    }
    colors = dark_colors if dark_mode else light_colors
    return colors.get(key, light_colors.get(key, ''))


# --- Selenium Script Import ---
try:
    from selenium_capture_logic import run_brave_screenshot_task
    SELENIUM_SCRIPT_AVAILABLE = True
except ImportError as e:
    print("***********************************************************************************")
    print(f"WARNING: Could not import 'selenium_capture_logic.py': {e}")
    print("The application will run in STUB mode for screenshot capture.")
    print("***********************************************************************************")
    SELENIUM_SCRIPT_AVAILABLE = False
    def run_brave_screenshot_task_stub():
        print("Starting STUBBED screenshot task...")
        time.sleep(0.5)
        dummy_image_path = "dummy_screenshot.png"
        try:
            img = Image.new('RGB', (800, 600), color='darkslategray')
            if PIL_TEXT_CAPABLE:
                draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 24)
                except IOError:
                    try: font = ImageFont.truetype("DejaVuSans.ttf", 24)
                    except IOError: font = ImageFont.load_default()
                draw.text((20, 20), "DUMMY SCREENSHOT (STUB MODE)", fill='white', font=font)
            img.save(dummy_image_path)
            print(f"Stub: Dummy screenshot saved: {dummy_image_path}")
            stub_dropdowns = [{"id": "dropdown_stub_1", "options": [{"text": "Stub Option A", "value": "valA"}, {"text": "Stub Option B", "value": "valB"}]}]
            return {"screenshot_path": dummy_image_path, "dropdowns_data": stub_dropdowns, "error": None}
        except Exception as e_stub_img:
            print(f"Stub: Failed to create dummy screenshot: {e_stub_img}")
            return {"screenshot_path": None, "dropdowns_data": [], "error": str(e_stub_img)}
    run_brave_screenshot_task = run_brave_screenshot_task_stub


# ============================================================================
# ICON SYSTEM FOR ACTIVITY LOG
# ============================================================================

class IconManager:
    """Manages loading and caching of icon files"""

    ICON_DIR = Path(__file__).parent / "icons"

    # Icon file mappings (emoji -> filename)
    ICON_FILES = {
        '🎉': 'success.png', '✅': 'success.png', '🧹': 'success.png', '✨': 'sparkles.png',
        '❌': 'error.png', '🚨': 'error.png',
        '⚠️': 'warning.png',
        '🔍': 'info.png', '📝': 'info.png', '📋': 'info.png', '🎨': 'info.png', '🔧': 'info.png',
        '⚡': 'progress.png', '🚀': 'progress.png', '🔄': 'progress.png', '⏳': 'progress.png',
        '💾': 'progress.png', '⬇️': 'progress.png',
        '🤖': 'ai.png', '💡': 'ai.png', '📜': 'ai.png',
        '📁': 'file.png', '📸': 'camera.png', '🖼️': 'file.png',
        '🌐': 'network.png', '📊': 'chart.png',
    }

    _cache = {}  # CTkImage cache

    @classmethod
    def load_icon(cls, emoji: str, size: tuple = (16, 16)) -> Optional[ctk.CTkImage]:
        """Load icon file and return CTkImage"""
        cache_key = f"{emoji}_{size[0]}x{size[1]}"

        # Return cached if available
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # Get icon filename
        icon_file = cls.ICON_FILES.get(emoji)
        if not icon_file:
            return None

        icon_path = cls.ICON_DIR / icon_file
        if not icon_path.exists():
            return None

        try:
            from PIL import Image
            pil_image = Image.open(icon_path)
            if pil_image.size != size:
                pil_image = pil_image.resize(size, Image.LANCZOS)

            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=size
            )
            cls._cache[cache_key] = ctk_image
            return ctk_image
        except Exception as e:
            return None

    @classmethod
    def load_all_icons(cls) -> dict:
        """Preload all icons into cache"""
        loaded = {}
        for emoji in cls.ICON_FILES.keys():
            icon = cls.load_icon(emoji)
            if icon:
                loaded[emoji] = icon
        if loaded:
            print(f"🔧 Loaded {len(loaded)}/{len(cls.ICON_FILES)} icon files")
        return loaded

    @classmethod
    def load_button_icon(cls, icon_name: str, size: tuple = (20, 20)) -> Optional[ctk.CTkImage]:
        """Load button icon at larger size (20x20) for workflow buttons"""
        cache_key = f"button_{icon_name}_{size[0]}x{size[1]}"

        # Return cached if available
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        icon_path = cls.ICON_DIR / icon_name
        if not icon_path.exists():
            print(f"⚠️ Button icon not found: {icon_path}")
            return None

        try:
            pil_image = Image.open(icon_path)
            pil_image.load()  # Force load to validate image
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            cls._cache[cache_key] = ctk_image
            return ctk_image
        except Exception as e:
            print(f"⚠️ Failed to load button icon {icon_name}: {e}")
            return None


class ErrorReporter:
    """Collects and packages error information for debugging"""

    @staticmethod
    def create_report(app_instance) -> dict:
        """Generate comprehensive error report"""
        import platform

        # Get screenshot data if available
        screenshot_data = None
        if hasattr(app_instance, 'current_image_path') and app_instance.current_image_path and os.path.exists(app_instance.current_image_path):
            try:
                with open(app_instance.current_image_path, 'rb') as f:
                    import base64
                    screenshot_data = base64.b64encode(f.read()).decode('utf-8')[:10000]
            except:
                screenshot_data = "[Failed to read screenshot]"

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": getattr(app_instance, 'current_version', 'Unknown'),
            "system": {
                "os": platform.system(),
                "os_version": platform.version(),
                "python_version": sys.version,
                "ctk_version": ctk.__version__
            },
            "screenshot": {
                "exists": bool(getattr(app_instance, 'current_image_path', None)),
                "path": str(app_instance.current_image_path) if hasattr(app_instance, 'current_image_path') and app_instance.current_image_path else None,
                "size": str(app_instance.original_pil_image_for_crop.size) if hasattr(app_instance, 'original_pil_image_for_crop') and app_instance.original_pil_image_for_crop else None,
                "preview": screenshot_data
            },
            "activity_log": app_instance.activity_log.log_entries[-50:] if hasattr(app_instance, 'activity_log') else [],
            "answer_text": app_instance.answer_textbox.get("1.0", "end")[:5000] if hasattr(app_instance, 'answer_textbox') else "",
            "last_error": str(getattr(app_instance, 'last_exception', None)),
            "model": app_instance.selected_model_var.get() if hasattr(app_instance, 'selected_model_var') else None,
            "api_key_present": bool(getattr(app_instance, 'api_key', None))
        }

    @staticmethod
    def save_report(report_data: dict, output_dir: str = ".") -> str:
        """Save report to JSON file"""
        filename = f"error_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        return filepath


def send_error_to_discord(report_data: dict, screenshot_path: str = None, answer_display_path: str = None) -> bool:
    """Send error report to Discord webhook automatically"""
    try:
        # Create Discord embed with error summary
        embed = {
            "title": "🚨 Homework Helper Error Report",
            "color": 0xFF0000,  # Red
            "fields": [
                {"name": "Version", "value": str(report_data.get("version", "Unknown")), "inline": True},
                {"name": "OS", "value": str(report_data.get("system", {}).get("os", "Unknown")), "inline": True},
                {"name": "Python", "value": str(report_data.get("system", {}).get("python_version", "Unknown"))[:50], "inline": True},
                {"name": "Timestamp", "value": str(report_data.get("timestamp", "Unknown")), "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add last error if available
        if "last_error" in report_data and report_data["last_error"] != "None":
            error_text = str(report_data["last_error"])[:1000]
            embed["description"] = f"**Last Error:**\n```{error_text}```"

        # Send embed
        response = requests.post(DISCORD_ERROR_WEBHOOK, json={"embeds": [embed]}, timeout=5)
        response.raise_for_status()

        # Upload full JSON as attachment
        json_bytes = json.dumps(report_data, indent=2, default=str).encode('utf-8')
        files = {"file": ("error_report.json", json_bytes)}
        response = requests.post(DISCORD_ERROR_WEBHOOK, files=files, timeout=10)
        response.raise_for_status()

        # Upload question screenshot if available
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                with open(screenshot_path, 'rb') as f:
                    screenshot_files = {"file": ("question_screenshot.png", f)}
                    requests.post(DISCORD_ERROR_WEBHOOK, files=screenshot_files, timeout=15)
            except Exception as e:
                print(f"⚠️ Could not upload question screenshot: {e}")

        # Upload answer display screenshot if available
        if answer_display_path and os.path.exists(answer_display_path):
            try:
                with open(answer_display_path, 'rb') as f:
                    answer_files = {"file": ("answer_display.png", f)}
                    requests.post(DISCORD_ERROR_WEBHOOK, files=answer_files, timeout=15)
            except Exception as e:
                print(f"⚠️ Could not upload answer display: {e}")
            finally:
                # Clean up temp file
                try:
                    os.remove(answer_display_path)
                except:
                    pass

        return True
    except Exception as e:
        print(f"⚠️ Could not send to Discord: {e}")
        return False


# Fallback symbols when icon files aren't available (clean Unicode, no brackets)
SYMBOL_MAP = {
    '🎉': '✓', '✅': '✓', '🧹': '✓',
    '❌': '✗', '🚨': '⚠', '⚠️': '⚠',
    '🔍': 'ℹ', '📝': 'ℹ', '📋': 'ℹ', '🎨': 'ℹ', '🔧': 'ℹ',
    '⚡': '↻', '🚀': '↻', '🔄': '↻', '⏳': '⋯', '💾': '💾', '⬇️': '↓',
    '🤖': '🤖', '💡': '💡', '📜': 'ℹ',
    '📁': '📁', '📸': '📷', '🌐': '🌐', '🖼️': '📁', '📊': 'ℹ', '✨': '✓',
}

# Emoji to color tag mapping
EMOJI_COLORS = {
    '🎉': 'SUCCESS', '✅': 'SUCCESS', '🧹': 'SUCCESS',
    '❌': 'ERROR', '🚨': 'CRITICAL',
    '⚠️': 'WARNING',
    '🔍': 'INFO_BLUE', '📝': 'INFO_BLUE', '📋': 'INFO_BLUE', '🎨': 'INFO_BLUE',
    '🔧': 'INFO_BLUE', '⚡': 'INFO_BLUE', '🚀': 'INFO_BLUE', '📁': 'INFO_BLUE', '📜': 'INFO_BLUE',
    '📸': 'INFO_BLUE',  # Camera icon for screenshots
    '🔄': 'INFO_CYAN', '⏳': 'INFO_CYAN', '💾': 'INFO_CYAN', '⬇️': 'INFO_CYAN',
    '🤖': 'INFO_PURPLE', '💡': 'INFO_PURPLE',
}

# Color values for text
COLOR_VALUES = {
    'SUCCESS': '#2ECC71',
    'ERROR': '#E74C3C',
    'CRITICAL': '#C0392B',
    'WARNING': '#F39C12',
    'INFO_BLUE': '#3498DB',
    'INFO_CYAN': '#1ABC9C',
    'INFO_PURPLE': '#9B59B6',
    'TIMESTAMP': 'gray60',
}


class ActivityLogWidget(ctk.CTkScrollableFrame):
    """Custom activity log with emoji icons and colored text"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.emoji_images = {}  # Cache loaded images
        self.log_entries = []  # Store plain text entries for copying
        self._load_emoji_images()

    def _load_emoji_images(self):
        """Load icon files using IconManager"""
        self.emoji_images = IconManager.load_all_icons()

    def add_log(self, message: str, emoji: str = None):
        """Add a log entry with optional emoji icon"""
        # Detect emoji from message start if not provided
        original_message = message
        if not emoji:
            for emoji_char in EMOJI_COLORS.keys():
                if message.startswith(emoji_char):
                    emoji = emoji_char
                    message = message[len(emoji_char):].lstrip()
                    break

        # Store plain text for copying (with emoji character if present)
        timestamp = time.strftime("[%H:%M:%S]")
        plain_text = f"{timestamp} {emoji if emoji else ''} {message}".strip()
        self.log_entries.append(plain_text)

        # Create log entry frame with context menu support
        entry_frame = ctk.CTkFrame(self, fg_color="transparent", height=20)
        entry_frame.pack(fill="x", pady=1, padx=2)
        entry_frame.pack_propagate(False)

        # Add right-click context menu for copying
        entry_frame.bind("<Button-3>", lambda e: self._show_context_menu(e))

        # Timestamp
        timestamp_label = ctk.CTkLabel(
            entry_frame,
            text=timestamp,
            font=("Consolas", 10),
            text_color=COLOR_VALUES['TIMESTAMP'],
            width=70,
            anchor="w"
        )
        timestamp_label.pack(side="left", padx=(2, 2))  # Reduced from (2, 5) to (2, 2)
        timestamp_label.bind("<Button-3>", lambda e: self._show_context_menu(e))

        # Icon display (use real icon file or fallback to colored symbol)
        if emoji and emoji in self.emoji_images:
            # Use icon image
            emoji_label = ctk.CTkLabel(
                entry_frame,
                text="",
                image=self.emoji_images[emoji],
                width=18
            )
            emoji_label.pack(side="left", padx=(0, 2))
            emoji_label.bind("<Button-3>", lambda e: self._show_context_menu(e))
        elif emoji:
            # Fallback to colored text symbol
            symbol = SYMBOL_MAP.get(emoji, '[?]')
            color_tag = EMOJI_COLORS.get(emoji, 'INFO_BLUE')
            symbol_color = COLOR_VALUES.get(color_tag, COLOR_VALUES['INFO_BLUE'])

            emoji_label = ctk.CTkLabel(
                entry_frame,
                text=symbol,
                font=("Consolas", 10, "bold"),
                text_color=symbol_color,
                width=18
            )
            emoji_label.pack(side="left", padx=(0, 2))
            emoji_label.bind("<Button-3>", lambda e: self._show_context_menu(e))

        # Message text
        color_tag = EMOJI_COLORS.get(emoji, 'INFO_BLUE')
        text_color = COLOR_VALUES.get(color_tag, COLOR_VALUES['INFO_BLUE'])

        message_label = ctk.CTkLabel(
            entry_frame,
            text=message,
            font=("Consolas", 10),
            text_color=text_color,
            anchor="w",
            justify="left"
        )
        message_label.pack(side="left", fill="x", expand=True)
        message_label.bind("<Button-3>", lambda e: self._show_context_menu(e))

        # Auto-scroll to bottom
        self.after(10, lambda: self._parent_canvas.yview_moveto(1.0))

    def _show_context_menu(self, event):
        """Show right-click context menu for copying logs"""
        import tkinter as tk
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy All Logs", command=self._copy_all_logs)
        menu.add_command(label="Clear Logs", command=self.clear)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _copy_all_logs(self):
        """Copy all log entries to clipboard"""
        if self.log_entries:
            all_logs = "\n".join(self.log_entries)
            self.clipboard_clear()
            self.clipboard_append(all_logs)
            print("📋 Activity log copied to clipboard")

    def clear(self):
        """Clear all log entries"""
        for widget in self.winfo_children():
            widget.destroy()
        self.log_entries.clear()


class SegmentedControl(ctk.CTkFrame):
    """iOS-style segmented control for workflow buttons"""

    def __init__(self, parent, buttons: List[Dict], **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.buttons = buttons
        self.button_widgets = []
        self._create_buttons()

    def _create_buttons(self):
        """Create segmented buttons with iOS styling"""
        num_buttons = len(self.buttons)

        for i, button_config in enumerate(self.buttons):
            # Determine corner rounding
            if num_buttons == 1:
                corner_radius = 8
            elif i == 0:
                # First button: rounded left only
                corner_radius = (8, 0, 0, 8)
            elif i == num_buttons - 1:
                # Last button: rounded right only
                corner_radius = (0, 8, 8, 0)
            else:
                # Middle buttons: no rounding
                corner_radius = 0

            # Create button with optional icon
            button_params = {
                "text": button_config.get("text", ""),
                "command": button_config.get("command", None),
                "height": 44,
                "font": ("Segoe UI", 12, "bold"),
                "fg_color": button_config.get("color", "#3498DB"),
                "hover_color": self._darken_color(button_config.get("color", "#3498DB")),
                "corner_radius": corner_radius if isinstance(corner_radius, int) else 8,
                "border_width": 1,
                "border_color": ("gray70", "gray30"),
                "state": button_config.get("state", "normal"),
                "text_color_disabled": button_config.get("text_color_disabled", ("gray74", "gray60"))
            }

            # Add icon if provided
            if "icon" in button_config and button_config["icon"] is not None:
                button_params["image"] = button_config["icon"]
                button_params["compound"] = "left"  # Icon on left, text on right

            btn = ctk.CTkButton(self, **button_params)

            # Pack with no padding between buttons
            btn.pack(side="left", fill="both", expand=True, padx=(0 if i > 0 else 0, 0))
            self.button_widgets.append(btn)

    def _darken_color(self, hex_color: str, amount: float = 0.15) -> str:
        """Darken a hex color by a percentage"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            # Convert to RGB
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Darken
            r = max(0, int(r * (1 - amount)))
            g = max(0, int(g * (1 - amount)))
            b = max(0, int(b * (1 - amount)))
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

    def set_button_state(self, index: int, state: str):
        """Enable/disable a button by index"""
        if 0 <= index < len(self.button_widgets):
            self.button_widgets[index].configure(state=state)


class WorkflowProgressDots(ctk.CTkFrame):
    """Progress indicator dots for 2-step workflow"""

    def __init__(self, parent, num_steps: int = 2, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.num_steps = num_steps
        self.current_step = 0
        self.dot_labels = []
        self._create_dots()

    def _create_dots(self):
        """Create progress dots"""
        for i in range(self.num_steps):
            dot_label = ctk.CTkLabel(
                self,
                text="●" if i == 0 else "○",
                font=("Arial", 16),
                text_color="#3498DB" if i == 0 else "gray60",
                width=20
            )
            dot_label.pack(side="left", padx=3)
            self.dot_labels.append(dot_label)

    def set_step(self, step: int):
        """Update which step is current (0-indexed)"""
        if 0 <= step < self.num_steps:
            self.current_step = step
            for i, dot_label in enumerate(self.dot_labels):
                if i == step:
                    dot_label.configure(text="●", text_color="#3498DB")
                else:
                    dot_label.configure(text="○", text_color="gray60")


class StdoutRedirector:
    """Stdout redirector that routes print() to ActivityLogWidget with emoji icons"""

    def __init__(self, activity_log_widget, app_instance):
        self.activity_log = activity_log_widget
        self.app = app_instance

    def write(self, string):
        """Write output to activity log"""
        self.app.after(0, self._write_to_log, string)

    def _write_to_log(self, string):
        """Add message to activity log with emoji detection"""
        # Skip empty strings and newlines
        if not string or string == '\n':
            return

        # Clean string
        message = string.strip()
        if not message:
            return

        # The ActivityLogWidget will automatically detect and handle emojis
        self.activity_log.add_log(message)

    def flush(self):
        """Required for sys.stdout compatibility"""
        pass

HANDLE_SIZE = 10
MIN_SELECTION_SIZE = 10
CONFIG_FILE = "config.json"

# Available vision models for homework analysis
AVAILABLE_MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen-2.5-vl-72b-instruct:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free",
    "qwen/qwen-2.5-vl-32b-instruct:free",
    "google/gemini-2.5-pro"
]

# Model display names with pricing indicators
MODEL_DISPLAY_NAMES = {
    "google/gemini-2.5-flash": "Gemini 2.5 Flash • Paid (Best Balance)",
    "google/gemini-2.0-flash-exp:free": "Gemini 2.0 Flash • FREE",
    "qwen/qwen-2.5-vl-72b-instruct:free": "Qwen 2.5 VL 72B • FREE (Most Capable)",
    "meta-llama/llama-3.2-11b-vision-instruct:free": "Llama 3.2 11B Vision • FREE",
    "qwen/qwen-2.5-vl-32b-instruct:free": "Qwen 2.5 VL 32B • FREE",
    "google/gemini-2.5-pro": "Gemini 2.5 Pro • Paid (Premium)"
}

# Default model for best balance of accuracy and cost
DEFAULT_MODEL = "google/gemini-2.5-flash"

def get_openrouter_response_streaming(api_key: str, model_name: str, image_base64: str, prompt_text: str, chunk_callback=None) -> dict:
    """
    Call OpenRouter API with STREAMING enabled for 1-3s time-to-first-token.
    Uses Server-Sent Events (SSE) per openrouter_api_stream.md
    """
    if not api_key:
        return {"status": "ERROR_PROCESSING_FAILED", "error_message": "API Key not provided"}

    effective_model = model_name if model_name in AVAILABLE_MODELS else DEFAULT_MODEL
    
    try:
        print(f"🚀 Streaming from OpenRouter API. Model: {effective_model}")
        
        # Construct messages with pre-encoded image
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/homework-helper",
            "X-Title": "Homework Helper AI"
        }
        
        payload = {
            "model": effective_model,
            "messages": messages,
            "temperature": 0.7,
            "stream": True,  # Enable streaming!
            "response_format": {"type": "json_object"}
        }
        
        print("📡 Sending streaming request...")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True,  # Enable streaming!
            timeout=120
        )
        
        response.raise_for_status()
        
        # SSE streaming parser (per openrouter_api_stream.md)
        buffer = ""
        accumulated_content = ""
        usage_data = {}
        generation_id = None  # Store generation ID for cost lookup
        first_token_received = False

        print("⚡ Streaming started, waiting for first token...")

        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if not chunk:
                continue

            buffer += chunk

            while True:
                line_end = buffer.find('\n')
                if line_end == -1:
                    break

                line = buffer[:line_end].strip()
                buffer = buffer[line_end + 1:]

                # Ignore SSE comments
                if line.startswith(':'):
                    continue

                if line.startswith('data: '):
                    data_str = line[6:]

                    if data_str == '[DONE]':
                        print("✅ Streaming complete")
                        break

                    try:
                        chunk_data = json.loads(data_str)

                        # Extract generation ID from first chunk (for cost lookup)
                        if not generation_id and 'id' in chunk_data:
                            generation_id = chunk_data['id']
                            print(f"📋 Generation ID: {generation_id}")

                        # Check for mid-stream error
                        if 'error' in chunk_data:
                            error_msg = chunk_data['error'].get('message', 'Stream error')
                            print(f"❌ Stream error: {error_msg}")
                            return {"status": "ERROR_PROCESSING_FAILED", "error_message": error_msg}

                        # Extract content delta
                        delta = chunk_data.get('choices', [{}])[0].get('delta', {})
                        content_piece = delta.get('content', '')

                        if content_piece:
                            if not first_token_received:
                                print("⚡ FIRST TOKEN RECEIVED!")
                                first_token_received = True

                            accumulated_content += content_piece

                            # Call callback for UI update
                            if chunk_callback:
                                chunk_callback(content_piece, accumulated_content)

                        # Extract usage if present (comes at end)
                        if 'usage' in chunk_data:
                            usage_data = chunk_data['usage']
                            print(f"📊 Usage: {usage_data.get('total_tokens', 0)} tokens")

                    except json.JSONDecodeError:
                        pass  # Ignore malformed chunks
        
        # Fetch actual cost from OpenRouter generation metadata API with retry logic
        actual_cost = None
        if generation_id:
            # Retry up to 3 times with exponential backoff (0s, 1s, 2s)
            for attempt in range(3):
                try:
                    wait_time = attempt  # 0s on first attempt, 1s on second, 2s on third
                    if wait_time > 0:
                        time.sleep(wait_time)
                        print(f"🔄 Retrying metadata fetch (attempt {attempt+1}/3)...")
                    elif attempt == 0:
                        print(f"💰 Fetching actual cost for generation {generation_id}...")

                    gen_response = requests.get(
                        f"https://openrouter.ai/api/v1/generation?id={generation_id}",
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=10
                    )

                    if gen_response.status_code == 200:
                        gen_data = gen_response.json().get('data', {})
                        actual_cost = gen_data.get('total_cost')
                        if actual_cost is not None:
                            print(f"✅ Actual cost: ${actual_cost:.6f}")
                            usage_data['actual_cost'] = actual_cost
                            break  # Success - exit retry loop
                        else:
                            print("⚠️ Cost not yet available in generation metadata")
                            if attempt < 2:  # Not last attempt
                                continue
                    else:
                        print(f"⚠️ Failed to fetch generation metadata (HTTP {gen_response.status_code})")
                        if attempt < 2 and gen_response.status_code == 404:
                            continue  # Retry on 404
                        else:
                            break  # Don't retry on other errors
                except Exception as e:
                    print(f"⚠️ Error fetching actual cost: {e}")
                    if attempt < 2:
                        continue
                    break

        # Parse final accumulated JSON
        print("🔄 Parsing final response...")
        try:
            parsed_content = json.loads(accumulated_content)

            # Normalize response: some models return array directly instead of object
            if isinstance(parsed_content, list):
                print(f"   ℹ️ Model returned array directly, wrapping in standard structure")
                parsed_content = {
                    "identified_question": "",
                    "answers": parsed_content,
                    "status": "SUCCESS"
                }

            # Ensure all models have consistent required fields
            if 'identified_question' not in parsed_content:
                parsed_content['identified_question'] = ""
            if 'answers' not in parsed_content:
                parsed_content['answers'] = []
            if 'status' not in parsed_content:
                parsed_content['status'] = "SUCCESS"

            # Add metadata
            parsed_content['_usage_data'] = usage_data
            parsed_content['_generation_id'] = generation_id
            return parsed_content
        except json.JSONDecodeError as e:
            return {
                "status": "ERROR_PROCESSING_FAILED",
                "error_message": f"JSON parsing error: {e}",
                "_usage_data": usage_data,
                "_generation_id": generation_id
            }
    
    except requests.exceptions.Timeout:
        return {"status": "ERROR_PROCESSING_FAILED", "error_message": "Request timed out"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {"status": "ERROR_PROCESSING_FAILED", "error_message": "Invalid API key"}
        elif e.response.status_code == 429:
            # Parse cooldown period from OpenRouter response
            cooldown_seconds = None
            try:
                error_data = e.response.json()
                # OpenRouter typically returns cooldown info in error.metadata.cooldown_seconds
                if 'error' in error_data and 'metadata' in error_data['error']:
                    cooldown_seconds = error_data['error']['metadata'].get('cooldown_seconds')

                # Fallback: parse from Retry-After header if available
                if cooldown_seconds is None and 'Retry-After' in e.response.headers:
                    try:
                        cooldown_seconds = int(e.response.headers['Retry-After'])
                    except ValueError:
                        pass
            except:
                pass

            if cooldown_seconds:
                error_msg = f"RATE_LIMIT|{cooldown_seconds}"
            else:
                error_msg = "RATE_LIMIT|60"  # Default to 60 seconds if not specified

            return {"status": "ERROR_RATE_LIMITED", "error_message": error_msg, "cooldown_seconds": cooldown_seconds or 60}
        elif e.response.status_code == 404:
            return {"status": "ERROR_MODEL_NOT_FOUND", "error_message": "Model no longer exists."}
        return {"status": "ERROR_PROCESSING_FAILED", "error_message": f"HTTP {e.response.status_code}"}
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        traceback.print_exc()
        return {"status": "ERROR_PROCESSING_FAILED", "error_message": str(e)}


class UpdateModal(ctk.CTkToplevel):
    """Modal window for displaying update progress with progress bar and restart button"""

    # Badge colors (GitHub-style)
    BADGE_COLORS = {
        'NEW': '#1a73e8',      # Blue
        'FIX': '#34a853',      # Green
        'CRITICAL': '#ea4335', # Red
        'UPDATE': '#fbbc04',   # Yellow
        'SECURITY': '#ff6b35',  # Orange
    }

    def __init__(self, parent, version: str, changelog: list):
        super().__init__(parent)

        self.parent = parent
        self.version = version
        self.changelog = changelog
        self.update_complete = False

        # Detect emoji font based on platform
        self.emoji_font = "Segoe UI Emoji" if platform.system() == "Windows" else "Apple Color Emoji"
        self.default_font = "Segoe UI" if platform.system() == "Windows" else "Arial"

        # Detect if this update contains critical fixes
        self.has_critical_fixes = any(
            "CRITICAL FIX:" in change or "CRITICAL:" in change
            for change in self.changelog
        )

        # Detect if this update contains security fixes
        self.has_security_fixes = any(
            "SECURITY:" in change or "SECURITY FIX:" in change
            for change in self.changelog
        )

        # Load icons for UpdateModal
        self.celebration_icon = IconManager.load_icon('celebration.png')
        self.clipboard_icon = IconManager.load_icon('clipboard.png')
        self.download_icon = IconManager.load_icon('download.png')
        self.restart_icon = IconManager.load_icon('restart.png')
        self.success_icon = IconManager.load_icon('success.png')
        self.error_icon = IconManager.load_icon('error.png')

        # Configure window
        self.title("Update Available")
        self.geometry("600x520")
        self.resizable(False, False)

        # Make modal (stay on top)
        self.transient(parent)
        self.grab_set()

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (520 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _extract_badge_type(self, text: str) -> Tuple[Optional[str], str]:
        """Extract badge type from changelog text (e.g., 'NEW: ...' returns ('NEW', '...')"""
        for badge_type in self.BADGE_COLORS.keys():
            prefix = f"{badge_type}: "
            if text.startswith(prefix):
                return badge_type, text[len(prefix):]
        return None, text

    def _create_badge(self, parent, badge_type: str) -> ctk.CTkFrame:
        """Create a GitHub-style pill badge"""
        badge_frame = ctk.CTkFrame(
            parent,
            fg_color=self.BADGE_COLORS[badge_type],
            corner_radius=10,
            height=20
        )

        label = ctk.CTkLabel(
            badge_frame,
            text=badge_type,
            font=(self.default_font, 9, "bold"),
            text_color="white",
            height=20
        )
        label.pack(padx=8, pady=2)

        return badge_frame

    def _build_ui(self):
        """Build the modal UI"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header with icon and version
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        # Icon
        if self.celebration_icon:
            icon_label = ctk.CTkLabel(
                header_frame,
                image=self.celebration_icon,
                text=""
            )
            icon_label.pack(side="left", padx=(0, 8))

        # Title text
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Update Available: v{self.version}",
            font=(self.default_font, 20, "bold"),
            text_color="#1a73e8"
        )
        title_label.pack(side="left")

        # Critical update badge (if applicable)
        if self.has_critical_fixes:
            critical_badge = ctk.CTkFrame(
                header_frame,
                fg_color="#ea4335",  # Red
                corner_radius=12,
                height=28
            )
            critical_badge.pack(side="left", padx=(10, 0))

            badge_label = ctk.CTkLabel(
                critical_badge,
                text="⚠️ CRITICAL",
                font=(self.default_font, 11, "bold"),
                text_color="white"
            )
            badge_label.pack(padx=10, pady=4)

        # Security update badge (if applicable)
        if self.has_security_fixes:
            security_badge = ctk.CTkFrame(
                header_frame,
                fg_color="#ff6b35",  # Orange
                corner_radius=12,
                height=28
            )
            security_badge.pack(side="left", padx=(10, 0))

            badge_label = ctk.CTkLabel(
                security_badge,
                text="🔒 SECURITY",
                font=(self.default_font, 11, "bold"),
                text_color="white"
            )
            badge_label.pack(padx=10, pady=4)

        # Changelog section
        changelog_frame = ctk.CTkFrame(main_frame, fg_color="#2b2b2b", corner_radius=10)
        changelog_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Changelog header with icon
        changelog_header = ctk.CTkFrame(changelog_frame, fg_color="transparent")
        changelog_header.pack(fill="x", padx=15, pady=(15, 10))

        if self.clipboard_icon:
            icon_label = ctk.CTkLabel(
                changelog_header,
                image=self.clipboard_icon,
                text=""
            )
            icon_label.pack(side="left", padx=(0, 6))

        changelog_title = ctk.CTkLabel(
            changelog_header,
            text="What's New:",
            font=(self.default_font, 14, "bold"),
            anchor="w"
        )
        changelog_title.pack(side="left")

        # Scrollable changelog container
        changelog_scroll = ctk.CTkScrollableFrame(
            changelog_frame,
            fg_color="#1e1e1e",
            height=150
        )
        changelog_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Add changelog items with badges
        for item in self.changelog:
            badge_type, text = self._extract_badge_type(item)

            # Create item container
            item_frame = ctk.CTkFrame(changelog_scroll, fg_color="transparent")
            item_frame.pack(fill="x", pady=3, anchor="w")

            # Add badge if present
            if badge_type:
                badge = self._create_badge(item_frame, badge_type)
                badge.pack(side="left", padx=(0, 8))

            # Add bullet point and text
            item_text = ctk.CTkLabel(
                item_frame,
                text=f"• {text}" if not badge_type else text,
                font=(self.default_font, 12),
                anchor="w",
                wraplength=500,
                justify="left"
            )
            item_text.pack(side="left", fill="x", expand=True)

        # Progress section
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(0, 15))

        # Status container with icon
        self.status_container = ctk.CTkFrame(progress_frame, fg_color="transparent")
        self.status_container.pack(fill="x", pady=(0, 5))

        # Status icon
        self.status_icon_label = ctk.CTkLabel(
            self.status_container,
            image=self.download_icon if self.download_icon else None,
            text=""
        )
        self.status_icon_label.pack(side="left", padx=(0, 6))

        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_container,
            text="Preparing to download...",
            font=(self.default_font, 12),
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            mode="determinate",
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(0)

        # Progress percentage label
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=(self.default_font, 11),
            text_color="#888888"
        )
        self.progress_label.pack(anchor="e")

        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        # Cancel button (left side)
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel_update,
            width=120,
            height=35,
            fg_color="#444444",
            hover_color="#555555",
            font=(self.default_font, 12)
        )
        self.cancel_button.pack(side="left")

        # Restart button (right side) - initially disabled
        self.restart_button = ctk.CTkButton(
            button_frame,
            text="Restart Now",
            image=self.restart_icon if self.restart_icon else None,
            compound="left",
            command=self.restart_application,
            width=150,
            height=35,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            state="disabled",
            font=(self.default_font, 12)
        )
        self.restart_button.pack(side="right")

    def update_progress(self, current: int, total: int, filename: str, percentage: int):
        """Update progress bar and status label (thread-safe)"""
        def _update():
            # Update icon to download icon
            if self.download_icon:
                self.status_icon_label.configure(image=self.download_icon)
            # Update text
            self.status_label.configure(text=f"Downloading: {filename} ({current}/{total})")
            self.progress_bar.set(percentage / 100.0)
            self.progress_label.configure(text=f"{percentage}%")

        # Use after() to ensure thread safety
        self.after(0, _update)

    def mark_complete(self):
        """Mark update as complete and enable restart button"""
        def _complete():
            self.update_complete = True
            # Update icon to success icon
            if self.success_icon:
                self.status_icon_label.configure(image=self.success_icon)
            # Update text
            self.status_label.configure(text="Update installed successfully!")
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="100%")
            self.restart_button.configure(state="normal")
            self.cancel_button.configure(text="Later")

        self.after(0, _complete)

    def mark_failed(self, error_msg: str = "Update failed"):
        """Mark update as failed"""
        def _failed():
            # Update icon to error icon
            if self.error_icon:
                self.status_icon_label.configure(image=self.error_icon)
            # Update text
            self.status_label.configure(text=error_msg)
            self.cancel_button.configure(text="Close")

        self.after(0, _failed)

    def cancel_update(self):
        """Cancel/close the update modal"""
        if not self.update_complete:
            print("⚠️ Update cancelled by user")
        self.grab_release()
        self.destroy()

    def restart_application(self):
        """Restart the application"""
        self.grab_release()
        self.destroy()

        # Call parent's restart method
        if hasattr(self.parent, 'restart_application'):
            self.parent.restart_application()


class HomeworkApp(ctk.CTk):
    def __init__(self):
        # Set appearance BEFORE creating window for macOS compatibility
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        super().__init__()
        self.title("Homework Helper AI")
        self.geometry("1300x900")

        self.grid_columnconfigure(0, weight=1, minsize=320); self.grid_columnconfigure(1, weight=3); self.grid_rowconfigure(0, weight=1)
        self.api_key_var = ctk.StringVar(); self.selected_model_var = ctk.StringVar()
        self.visual_enhancement_enabled = ctk.BooleanVar(value=True)  # Toggle for visual enhancement
        self.original_pil_image_for_crop = None; self.displayed_ctk_image_size = None
        self.current_image_path = None; self.current_dropdown_data = []
        self.current_image_base64 = None  # Cached base64 encoding for performance
        self.current_image_base64_path = None  # Track which image the base64 cache is for
        self.crop_selection_coords = None; self.active_drag_mode = None
        self.drag_start_mouse_pos_relative_to_image = None; self.drag_start_selection_coords = None
        self.drag_start_mouse_root_pos = None
        
        # Session tracking
        self.session_api_calls = 0
        self.session_total_tokens = 0
        self.session_cost = 0.0
        self.account_balance = 0.0
        
        # Streaming state
        self.streaming_active = False
        self.accumulated_response = ""

        # Load button icons for workflow buttons
        self.button_capture_icon = IconManager.load_button_icon('button-capture.png', size=(20, 20))
        self.button_answer_icon = IconManager.load_button_icon('button-answer.png', size=(20, 20))

        # Load button icons for utility buttons
        self.brave_icon = IconManager.load_button_icon('brave.png', size=(20, 20))
        self.folder_icon = IconManager.load_button_icon('folder.png', size=(20, 20))
        self.warning_icon = IconManager.load_button_icon('warning.png', size=(20, 20))

        # Create left panel
        self.left_panel = ctk.CTkFrame(self, corner_radius=0)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        self.left_panel.grid_propagate(False); self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(0, weight=0); self.left_panel.grid_rowconfigure(1, weight=0); self.left_panel.grid_rowconfigure(2, weight=0); self.left_panel.grid_rowconfigure(3, weight=1, minsize=150)
        # === NEW BUTTON LAYOUT (v1.0.9) ===
        button_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        button_container.grid(row=0, column=0, sticky="new", padx=10, pady=(10, 10))
        button_container.grid_columnconfigure(0, weight=1)

        # Primary Workflow - Segmented Control (2 steps)
        workflow_buttons = [
            {
                "text": "Capture Question",
                "icon": self.button_capture_icon,
                "command": self.start_capture_thread,
                "color": "#3498DB",  # Blue
                "state": "normal",
                "text_color_disabled": "white"
            },
            {
                "text": "Get AI Answer",
                "icon": self.button_answer_icon,
                "command": self.start_ai_thread,
                "color": "#2ECC71",  # Green
                "state": "disabled",
                "text_color_disabled": "white"  # Keep text white when disabled
            }
        ]

        self.workflow_control = SegmentedControl(button_container, workflow_buttons)
        self.workflow_control.pack(fill="x", pady=(0, 5))

        # Store button references for easy access
        self.capture_button = self.workflow_control.button_widgets[0]
        self.ai_button = self.workflow_control.button_widgets[1]

        # Progress dots
        self.progress_dots = WorkflowProgressDots(button_container, num_steps=2)
        self.progress_dots.pack(pady=(3, 10))

        # Utility Buttons (smaller, de-emphasized)
        utility_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        utility_frame.pack(fill="x", pady=(5, 0))
        utility_frame.grid_columnconfigure(0, weight=1)
        utility_frame.grid_columnconfigure(1, weight=1)

        utility_font = ("Segoe UI", 10)
        utility_height = 32

        self.launch_brave_button = ctk.CTkButton(
            utility_frame,
            text="Launch Brave",
            image=self.brave_icon,
            compound="left",
            command=self.launch_brave_with_debugging,
            height=utility_height,
            font=utility_font,
            corner_radius=6,
            fg_color=("#FF8C00", "#FF6347"),
            hover_color=("#FF7F50", "#FF4500")
        )
        self.launch_brave_button.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")

        self.load_screenshot_button = ctk.CTkButton(
            utility_frame,
            text="Load Screenshot",
            image=self.folder_icon,
            compound="left",
            command=self.load_saved_screenshot,
            height=utility_height,
            font=utility_font,
            corner_radius=6,
            fg_color=("#4A90E2", "#2A5298"),
            hover_color=("#357ABD", "#1F4788")
        )
        self.load_screenshot_button.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="ew")

        # Report Error button (for debugging)
        self.report_error_button = ctk.CTkButton(
            utility_frame,
            text="Report Error",
            image=self.warning_icon,
            compound="left",
            command=self.create_error_report,
            height=utility_height,
            font=utility_font,
            corner_radius=6,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        self.report_error_button.grid(row=1, column=0, columnspan=2, padx=0, pady=(5, 0), sticky="ew")

        # Re-crop button will be added dynamically to screenshot area (not here)
        settings_outer_frame = ctk.CTkFrame(self.left_panel); settings_outer_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(10,5)); settings_outer_frame.grid_columnconfigure(0, weight=1)
        
        # Settings header with inline usage stats
        settings_header_frame = ctk.CTkFrame(settings_outer_frame, fg_color="transparent")
        settings_header_frame.pack(fill="x", pady=(5,10), padx=10)
        
        settings_label = ctk.CTkLabel(settings_header_frame, text="Settings", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        settings_label.pack(side="left", anchor="w")
        
        # Usage label on right side of Settings
        self.usage_label = ctk.CTkLabel(settings_header_frame, text="$0.00 • $0.00", font=("Segoe UI", 9), text_color=("gray50", "gray60"))
        self.usage_label.pack(side="right", anchor="e")
        api_key_frame = ctk.CTkFrame(settings_outer_frame, fg_color="transparent"); api_key_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(api_key_frame, text="API Key:", width=70, anchor="w").pack(side="left", padx=(0,5)); self.api_key_entry = ctk.CTkEntry(api_key_frame, textvariable=self.api_key_var, show="*"); self.api_key_entry.pack(side="left", fill="x", expand=True)
        model_frame = ctk.CTkFrame(settings_outer_frame, fg_color="transparent"); model_frame.pack(fill="x", padx=10, pady=2)
        # Create display values list with pricing indicators
        model_display_values = [MODEL_DISPLAY_NAMES.get(m, m) for m in AVAILABLE_MODELS]
        ctk.CTkLabel(model_frame, text="AI Model:", width=70, anchor="w").pack(side="left", padx=(0,5))
        self.model_combobox = ctk.CTkComboBox(
            model_frame,
            variable=self.selected_model_var,
            values=model_display_values,
            state="readonly",
            command=self._on_model_selection_change
        )
        self.model_combobox.pack(side="left", fill="x", expand=True)
        
        # Visual Enhancement Toggle
        visual_toggle_frame = ctk.CTkFrame(settings_outer_frame, fg_color="transparent")
        visual_toggle_frame.pack(fill="x", padx=10, pady=2)
        self.visual_toggle = ctk.CTkCheckBox(visual_toggle_frame, text="Enable Visual Grid (for drag-to-image)", variable=self.visual_enhancement_enabled, font=("Segoe UI", 9))
        self.visual_toggle.pack(side="left")
        
        self.load_config()
        self.save_settings_button = ctk.CTkButton(settings_outer_frame, text="Save Settings", command=self.save_config, height=30, font=("Segoe UI", 12)); self.save_settings_button.pack(pady=(10,10), padx=10, fill="x")
        
        self.log_label = ctk.CTkLabel(self.left_panel, text="Activity Log", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")); self.log_label.grid(row=2, column=0, padx=10, pady=(10,2), sticky="nw")

        # New Activity Log Widget with emoji icons (v1.0.9)
        self.activity_log = ActivityLogWidget(
            self.left_panel,
            border_width=1,
            border_color=("gray80", "gray25")
        )
        self.activity_log.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10))
        
        # Auto-check balance
        threading.Thread(target=self.refresh_account_balance, daemon=True).start()

        # Auto-check for updates
        threading.Thread(target=self.check_for_updates_on_startup, daemon=True).start()

        # Create right panel
        self.right_panel = ctk.CTkFrame(self, corner_radius=0)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1); self.right_panel.grid_rowconfigure(0, weight=3); self.right_panel.grid_rowconfigure(1, weight=2)
        self.screenshot_area_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent"); self.screenshot_area_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10,5))
        self.screenshot_area_frame.grid_columnconfigure(0, weight=1); self.screenshot_area_frame.grid_rowconfigure(0, weight=0); self.screenshot_area_frame.grid_rowconfigure(1, weight=1)
        self.screenshot_label_text = ctk.CTkLabel(self.screenshot_area_frame, text="Captured Screenshot", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")); self.screenshot_label_text.grid(row=0, column=0, padx=0, pady=(0,5), sticky="nw")
        self.screenshot_display_frame = ctk.CTkFrame(self.screenshot_area_frame, fg_color=("gray92", "gray17"), border_width=1, border_color=("gray80", "gray25")); self.screenshot_display_frame.grid(row=1, column=0, sticky="nsew")
        self.screenshot_display_frame.grid_propagate(False); self.screenshot_display_frame.grid_columnconfigure(0, weight=1); self.screenshot_display_frame.grid_rowconfigure(0, weight=1)
        self._create_screenshot_image_label_with_children()
        self.answer_list_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent"); self.answer_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5,10))
        self.answer_list_frame.grid_columnconfigure(0, weight=1); self.answer_list_frame.grid_rowconfigure(0, weight=0); self.answer_list_frame.grid_rowconfigure(1, weight=1)
        self.answer_list_label = ctk.CTkLabel(self.answer_list_frame, text="AI Generated Answers", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")); self.answer_list_label.grid(row=0, column=0, padx=0, pady=(5,5), sticky="nw")
        self.answer_scroll_frame = ctk.CTkScrollableFrame(self.answer_list_frame, border_width=1, border_color=("gray80", "gray25")); self.answer_scroll_frame.grid(row=1, column=0, sticky="nsew"); self.answer_scroll_frame.grid_columnconfigure(0, weight=1)
        self.initial_answer_message = ctk.CTkLabel(self.answer_scroll_frame, text="Answers will appear here.", text_color=("gray60", "gray40")); self.initial_answer_message.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # Redirect stdout/stderr to Activity Log (v1.0.9)
        sys.stdout = StdoutRedirector(self.activity_log, self)
        sys.stderr = StdoutRedirector(self.activity_log, self)

        if not SELENIUM_SCRIPT_AVAILABLE: print("NOTE: Running in STUB mode for screenshots.")
        if not AVAILABLE_MODELS: print("ERROR: No suitable AI models are configured..."); self.ai_button.configure(state="disabled", text="AI Model Error")

        self.update_idletasks()
        print("✅ GUI Initialized. Ready to capture.")

    def _get_model_id_from_display(self, display_name):
        """Convert display name back to model ID"""
        for model_id, display in MODEL_DISPLAY_NAMES.items():
            if display == display_name:
                return model_id
        return display_name  # Fallback to raw value

    def _get_display_from_model_id(self, model_id):
        """Convert model ID to display name"""
        return MODEL_DISPLAY_NAMES.get(model_id, model_id)

    def _on_model_selection_change(self, choice):
        """Handle model selection from dropdown"""
        # No action needed - the variable is already updated
        pass

    def load_config(self):
        # Load config file
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f: config = json.load(f)
                self.api_key_var.set(config.get("api_key", ""))
                loaded_model_id = config.get("selected_model", DEFAULT_MODEL)

                # Convert model ID to display name for the combobox
                loaded_display_name = self._get_display_from_model_id(loaded_model_id)

                if loaded_display_name in self.model_combobox.cget("values"):
                    self.selected_model_var.set(loaded_display_name)
                elif self._get_display_from_model_id(DEFAULT_MODEL) in self.model_combobox.cget("values"):
                    self.selected_model_var.set(self._get_display_from_model_id(DEFAULT_MODEL))
                    print(f"Warning: Saved model '{loaded_model_id}' invalid, using default.")
                elif self.model_combobox.cget("values"):
                    self.selected_model_var.set(self.model_combobox.cget("values")[0])
                    print(f"Warning: Saved model '{loaded_model_id}' and default invalid, using first available.")
                else: print(f"ERROR: No models in combobox."); self.selected_model_var.set("")
                print("✅ Configuration loaded.")
            else:
                self.api_key_var.set("")
                default_display = self._get_display_from_model_id(DEFAULT_MODEL)
                if default_display in self.model_combobox.cget("values"):
                    self.selected_model_var.set(default_display)
                elif self.model_combobox.cget("values"):
                    self.selected_model_var.set(self.model_combobox.cget("values")[0])
                else: self.selected_model_var.set("")
                print(f"ℹ️ No config file found. Using defaults.")
        except Exception as e: print(f"Error loading config: {e}"); traceback.print_exc(); self.api_key_var.set(""); self.selected_model_var.set(DEFAULT_MODEL if DEFAULT_MODEL in self.model_combobox.cget("values") else (self.model_combobox.cget("values")[0] if self.model_combobox.cget("values") else ""))

    def save_config(self):
        # Convert display name back to model ID for saving
        display_name = self.selected_model_var.get()
        model_id = self._get_model_id_from_display(display_name)

        config = {"api_key": self.api_key_var.get(), "selected_model": model_id}
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(config, f, indent=4)
            print("✅ Configuration saved."); self.save_settings_button.configure(text="Settings Saved!", fg_color="green")
            self.after(2000, lambda: self.save_settings_button.configure(text="Save Settings", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))
            threading.Thread(target=self.refresh_account_balance, daemon=True).start()
        except Exception as e: print(f"Error saving config: {e}"); self.save_settings_button.configure(text="Save Failed!", fg_color="red"); self.after(2000, lambda: self.save_settings_button.configure(text="Save Settings", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))
    
    def refresh_account_balance(self):
        """Fetch OpenRouter account balance using /api/v1/credits endpoint"""
        api_key = self.api_key_var.get()
        if not api_key:
            self.account_balance = 0.0
            self._update_usage_display()
            return

        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            # Use correct credits endpoint per documentation
            response = requests.get("https://openrouter.ai/api/v1/credits", headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json().get("data", {})
                total_credits = data.get("total_credits", 0)
                total_usage = data.get("total_usage", 0)
                remaining = total_credits - total_usage

                self.account_balance = remaining
                self._update_usage_display()
                print(f"✅ Balance: ${remaining:.2f}")
            elif response.status_code == 401:
                print("⚠️ Invalid API key")
                self.account_balance = 0.0
                self._update_usage_display()
            else:
                print(f"⚠️ Balance check failed: {response.status_code}")
                self.account_balance = 0.0
                self._update_usage_display()
        except Exception as e:
            self.account_balance = 0.0
            self._update_usage_display()
            print(f"Balance check error: {e}")

    def check_for_updates_on_startup(self):
        """Check for application updates on startup"""
        if not AUTO_UPDATER_AVAILABLE:
            return

        try:
            # Small delay to let the UI load first
            time.sleep(2)

            update_available, new_version, changelog = check_for_updates_silent()

            if update_available:
                print(f"🎉 Update available: v{new_version}")

                # Show update modal on main thread
                self.after(0, lambda: self._show_update_modal(new_version, changelog))
            else:
                print("✅ Application is up to date")

        except Exception as e:
            print(f"⚠️ Update check failed: {e}")

    def _show_update_modal(self, version: str, changelog: list):
        """Show update modal and handle update process"""
        try:
            # Create modal
            modal = UpdateModal(self, version, changelog)

            # Force modal to render and become visible
            modal.update_idletasks()
            modal.focus_force()

            # Start update in background thread with delay
            def perform_update():
                try:
                    # Wait for modal to fully render and become visible (critical!)
                    time.sleep(1.0)

                    # Progress callback
                    def on_progress(current, total, filename, percentage):
                        modal.update_progress(current, total, filename, percentage)

                    # Apply update with progress callback
                    success = apply_update_silent(progress_callback=on_progress)

                    if success:
                        modal.mark_complete()
                        print("✅ Update installed! Click 'Restart Now' to use the new version.")
                    else:
                        modal.mark_failed("Update download failed")
                        print("⚠️ Update download failed. You can try again later.")

                except Exception as e:
                    modal.mark_failed(f"Error: {str(e)}")
                    print(f"❌ Update error: {e}")

            # Start update thread after modal is fully rendered
            threading.Thread(target=perform_update, daemon=True).start()

        except Exception as e:
            print(f"❌ Failed to show update modal: {e}")

    def restart_application(self):
        """Restart the application after update"""
        try:
            print("🔄 Restarting application...")

            # Save current state if needed
            self.quit()

            # Get the current Python executable and script
            python = sys.executable
            script = sys.argv[0]

            # Restart using the same Python executable
            os.execv(python, [python, script] + sys.argv[1:])

        except Exception as e:
            print(f"❌ Restart failed: {e}")
            print("Please restart the application manually.")

    def update_session_usage(self, tokens_used: dict):
        """Update session cost with ACTUAL cost from OpenRouter (not estimated)"""
        self.session_api_calls += 1
        self.session_total_tokens += tokens_used.get("total_tokens", 0)

        # Use actual cost from OpenRouter generation metadata if available
        if 'actual_cost' in tokens_used and tokens_used['actual_cost'] is not None:
            actual_cost = tokens_used['actual_cost']
            self.session_cost += actual_cost  # Accumulate actual costs
            print(f"Session: {self.session_api_calls} calls, ${self.session_cost:.6f} (actual cost: ${actual_cost:.6f})")
        else:
            # Fallback to estimation only if actual cost unavailable
            estimated_cost = (self.session_total_tokens / 1000000) * 0.50
            self.session_cost = estimated_cost
            print(f"Session: {self.session_api_calls} calls, ~${estimated_cost:.4f} (estimated)")

        self._update_usage_display()
    
    def _update_usage_display(self):
        """Update the inline usage label (Balance • Session)"""
        balance_text = f"${self.account_balance:.2f}" if self.account_balance > 0 else "$0.00"
        session_text = f"${self.session_cost:.4f}" if self.session_cost > 0 else "$0.00"
        
        # Simple format: $X.XX • $Y.YY
        combined_text = f"{balance_text} • {session_text}"
        
        # Color based on balance
        if self.account_balance > 1:
            text_color = ("#4CAF50", "#66BB6A")
        elif self.account_balance > 0.1:
            text_color = ("#FF9800", "#FFB74D")
        else:
            text_color = ("#F44336", "#EF5350")
        
        self.usage_label.configure(text=combined_text, text_color=text_color)

    def launch_brave_with_debugging(self):
        """Launch Brave browser with remote debugging enabled."""
        self.launch_brave_button.configure(state="disabled", text="Launching Brave...")
        print("Launching Brave browser with remote debugging...")
        
        brave_exe_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        user_data_dir = r"C:\temp\brave_debug"
        
        # Create user data directory if it doesn't exist
        try:
            os.makedirs(user_data_dir, exist_ok=True)
            print(f"Created/verified user data directory: {user_data_dir}")
        except Exception as e:
            print(f"Warning: Could not create user data directory: {e}")
        
        # Launch Brave with debugging parameters
        launch_args = [
            brave_exe_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={user_data_dir}",
            "--disable-features=VizDisplayCompositor"
        ]
        
        try:
            subprocess.Popen(launch_args, shell=False)
            print("✅ Brave browser launched successfully with remote debugging enabled!")
            print("🌐 Navigate to your homework site and then click 'Capture Question'")
            self.launch_brave_button.configure(text="Brave Launched ✓", fg_color="green")
            self.after(3000, lambda: self.launch_brave_button.configure(text="Launch Brave", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))
        except FileNotFoundError:
            print("❌ Error: Brave browser not found at expected location.")
            print(f"   Expected path: {brave_exe_path}")
            print("   Please ensure Brave is installed or update the path in the code.")
            self.launch_brave_button.configure(text="Brave Not Found ✗", fg_color="red")
            self.after(3000, lambda: self.launch_brave_button.configure(text="Launch Brave", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))
        except Exception as e:
            print(f"❌ Error launching Brave: {e}")
            self.launch_brave_button.configure(text="Launch Failed ✗", fg_color="red")
            self.after(3000, lambda: self.launch_brave_button.configure(text="Launch Brave", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))
        finally:
            self.after(1000, lambda: self.launch_brave_button.configure(state="normal"))

    def load_saved_screenshot(self):
        """Load a saved screenshot for testing purposes."""
        print("Opening file dialog to select screenshot...")
        
        # Define the saved_screenshots directory path
        saved_screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "HW Helper Modern", "saved_screenshots")
        
        # Check if the directory exists, otherwise use current directory
        if not os.path.exists(saved_screenshots_dir):
            saved_screenshots_dir = os.getcwd()
            print(f"Saved screenshots directory not found, using: {saved_screenshots_dir}")
        else:
            saved_screenshots_dir = os.path.abspath(saved_screenshots_dir)
            print(f"Using saved screenshots directory: {saved_screenshots_dir}")
        
        # Open file dialog to select image
        file_path = filedialog.askopenfilename(
            title="Select Screenshot to Load",
            initialdir=saved_screenshots_dir,
            filetypes=[
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg;*.jpeg"),
                ("All Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            print("No file selected.")
            return
        
        print(f"Selected file: {file_path}")
        
        try:
            # Check if there's an associated JSON data file
            base_name = os.path.splitext(file_path)[0]
            json_data_path = f"{base_name}_data.json"
            
            dropdown_data = []
            if os.path.exists(json_data_path):
                print(f"Found associated data file: {json_data_path}")
                try:
                    with open(json_data_path, 'r') as f:
                        saved_data = json.load(f)
                        dropdown_data = saved_data.get("dropdown_data", [])
                        if dropdown_data:
                            print(f"Loaded {len(dropdown_data)} dropdown(s) from saved data")
                except Exception as e:
                    print(f"Warning: Could not load JSON data: {e}")
            
            # Load the image
            pil_image = Image.open(file_path)
            img_width, img_height = pil_image.size
            print(f"📸 NEW SCREENSHOT LOADED: {img_width}x{img_height}")
            
            # CRITICAL: Clear ALL previous state before setting new data
            self._clear_answers()
            self.current_image_base64 = None  # Force re-encoding
            self.current_image_base64_path = None  # Clear path tracking
            self.accumulated_response = ""
            self.streaming_active = False
            
            print(f"🧹 Cleared all previous state for fresh analysis")
            
            # Update the application state with NEW data
            self.current_image_path = os.path.abspath(file_path)
            self.original_pil_image_for_crop = pil_image.copy()
            self.current_dropdown_data = dropdown_data
            
            # Update the display
            self._update_screenshot_display(pil_image)
            self._update_answer_textbox(f"Loaded: {os.path.basename(file_path)}", False)
            
            print(f"✅ Screenshot loaded successfully: {os.path.basename(file_path)}")
            
        except Exception as e:
            error_msg = f"Error loading screenshot: {e}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            self._update_screenshot_display(None, error_msg)
            self.current_image_path = None

    def _capture_answer_display(self) -> Optional[str]:
        """
        Capture answer display area as PNG - SECURE widget render (no screen capture)

        Security: Does NOT use screen coordinates or PIL.ImageGrab.
        Only renders the widget tree internally - no external windows can be captured.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            widget = self.answer_scroll_frame
            widget.update_idletasks()

            # Get widget dimensions
            width = max(widget.winfo_width(), 400)  # Minimum width for readability
            height = max(widget.winfo_height(), 300)  # Minimum height

            # Create blank image with dark background
            img = Image.new('RGB', (width, height), color='#1e1e1e')
            draw = ImageDraw.Draw(img)

            # Try to load a basic font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 11)
                font_bold = ImageFont.truetype("arialbd.ttf", 12)
            except:
                font = ImageFont.load_default()
                font_bold = font

            def render_widget(w, x_offset=0, y_offset=0):
                """Recursively render widget content to PIL image"""
                try:
                    # Get widget position and dimensions
                    try:
                        rel_x = w.winfo_x()
                        rel_y = w.winfo_y()
                        w_width = w.winfo_width()
                        w_height = w.winfo_height()
                    except:
                        return  # Widget not rendered yet

                    abs_x = x_offset + rel_x
                    abs_y = y_offset + rel_y

                    # Skip if outside bounds
                    if abs_x >= width or abs_y >= height or abs_x + w_width < 0 or abs_y + w_height < 0:
                        return

                    # Render based on widget type
                    widget_class = w.__class__.__name__

                    if 'Label' in widget_class:
                        # Render text labels
                        try:
                            text = w.cget("text")
                            if text and text.strip():
                                text_color = 'white'
                                try:
                                    color_cfg = w.cget("text_color")
                                    if isinstance(color_cfg, str):
                                        text_color = color_cfg
                                    elif isinstance(color_cfg, tuple):
                                        text_color = color_cfg[0]
                                except:
                                    pass

                                # Truncate very long text
                                if len(text) > 100:
                                    text = text[:97] + "..."

                                draw.text((abs_x + 5, abs_y + 3), text, fill=text_color, font=font)
                        except:
                            pass

                    elif 'Frame' in widget_class:
                        # Render frame backgrounds
                        try:
                            fg_color = w.cget("fg_color")
                            if fg_color and fg_color != "transparent":
                                color = fg_color
                                if isinstance(fg_color, tuple):
                                    color = fg_color[0]

                                # Draw rectangle
                                draw.rectangle(
                                    [abs_x, abs_y, min(abs_x + w_width, width-1), min(abs_y + w_height, height-1)],
                                    fill=color
                                )
                        except:
                            pass

                    # Recursively render children
                    try:
                        for child in w.winfo_children():
                            render_widget(child, abs_x, abs_y)
                    except:
                        pass

                except Exception:
                    # Skip widgets that cause errors
                    pass

            # Render the entire widget tree
            render_widget(widget)

            # Add watermark to indicate this is a secure render
            draw.text((5, height - 20), "Secure Widget Render (No Screen Capture)", fill='#666666', font=font)

            # Save to temp file
            temp_path = f"./temp_answer_display_{int(time.time())}.png"
            img.save(temp_path)
            return temp_path

        except Exception as e:
            print(f"⚠️ Could not capture answer display: {e}")
            return None

    def create_error_report(self):
        """Generate and send error report automatically"""
        try:
            print("📤 Sending error report to developer...")

            # Create report
            report = ErrorReporter.create_report(self)

            # Capture answer display as PNG
            answer_screenshot_path = self._capture_answer_display()

            # Send to Discord (screenshot + answer_display_screenshot)
            screenshot_path = self.current_image_path if hasattr(self, 'current_image_path') else None
            success = send_error_to_discord(report, screenshot_path, answer_screenshot_path)

            if success:
                print("✅ Error report sent automatically!")
            else:
                print("❌ Could not send report - check network connection")

        except Exception as e:
            print(f"❌ Error reporting failed: {e}")
            import traceback
            traceback.print_exc()

    def _create_screenshot_image_label_with_children(self):
        if hasattr(self, 'screenshot_image_label') and self.screenshot_image_label.winfo_exists():
            if hasattr(self, 'selection_rect_visual') and self.selection_rect_visual.winfo_exists(): self.selection_rect_visual.destroy()
            if hasattr(self, 'handles'):
                for handle_widget in self.handles.values():
                    if handle_widget.winfo_exists(): handle_widget.destroy()
            if hasattr(self, 'overlay_top') and self.overlay_top.winfo_exists(): self.overlay_top.destroy()
            if hasattr(self, 'overlay_bottom') and self.overlay_bottom.winfo_exists(): self.overlay_bottom.destroy()
            if hasattr(self, 'overlay_left') and self.overlay_left.winfo_exists(): self.overlay_left.destroy()
            if hasattr(self, 'overlay_right') and self.overlay_right.winfo_exists(): self.overlay_right.destroy()
            self.handles = {}
            self.screenshot_image_label.destroy()

        self.screenshot_image_label = ctk.CTkLabel(self.screenshot_display_frame, text="No image captured.", corner_radius=0)
        self.screenshot_image_label.image = None # type: ignore
        self.screenshot_image_label.grid(row=0, column=0, sticky="nsew")
        overlay_color = ("gray40", "gray25") 
        self.overlay_top = ctk.CTkFrame(self.screenshot_image_label, fg_color=overlay_color, corner_radius=0)
        self.overlay_bottom = ctk.CTkFrame(self.screenshot_image_label, fg_color=overlay_color, corner_radius=0)
        self.overlay_left = ctk.CTkFrame(self.screenshot_image_label, fg_color=overlay_color, corner_radius=0)
        self.overlay_right = ctk.CTkFrame(self.screenshot_image_label, fg_color=overlay_color, corner_radius=0)
        self.selection_rect_visual = ctk.CTkFrame(self.screenshot_image_label, fg_color="transparent", border_width=2, border_color="cyan", corner_radius=0)
        self.handles = {}
        handle_positions = ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT", "MID_TOP", "MID_BOTTOM", "MID_LEFT", "MID_RIGHT"]
        for pos in handle_positions:
            handle = ctk.CTkFrame(self.screenshot_image_label, width=HANDLE_SIZE, height=HANDLE_SIZE, fg_color="cyan", border_width=1, border_color="black", corner_radius=0)
            self.handles[pos] = handle
            handle.bind("<ButtonPress-1>", lambda event, p=pos: self.on_handle_press(event, p))
            handle.bind("<B1-Motion>", self.on_handle_drag)
            handle.bind("<ButtonRelease-1>", self.on_mouse_release_any)
        self.screenshot_image_label.bind("<ButtonPress-1>", self.on_image_area_press)
        self.screenshot_image_label.bind("<B1-Motion>", self.on_image_area_drag)
        self.screenshot_image_label.bind("<ButtonRelease-1>", self.on_mouse_release_any)
        self._hide_crop_visuals()

    def _hide_crop_visuals(self):
        if hasattr(self, 'selection_rect_visual'): self.selection_rect_visual.place_forget()
        if hasattr(self, 'handles'):
            for handle in self.handles.values(): handle.place_forget()
        if hasattr(self, 'overlay_top'): self.overlay_top.place_forget()
        if hasattr(self, 'overlay_bottom'): self.overlay_bottom.place_forget()
        if hasattr(self, 'overlay_left'): self.overlay_left.place_forget()
        if hasattr(self, 'overlay_right'): self.overlay_right.place_forget()
        if hasattr(self, 'recrop_button'): self.recrop_button.configure(state="disabled")
        is_image_present = hasattr(self.screenshot_image_label, 'image') and self.screenshot_image_label.image is not None # type: ignore
        if not self.current_image_path or not os.path.exists(self.current_image_path) or not is_image_present: self.ai_button.configure(state="disabled")
        self.crop_selection_coords = None; self.active_drag_mode = None

    def _update_crop_visuals(self):
        if not self.crop_selection_coords or not self.displayed_ctk_image_size:
            self._hide_crop_visuals(); return
        img_w, img_h = self.displayed_ctk_image_size
        r_x1, r_y1, r_x2, r_y2 = self.crop_selection_coords
        x1, y1 = min(r_x1, r_x2), min(r_y1, r_y2); x2, y2 = max(r_x1, r_x2), max(r_y1, r_y2)
        x1, y1 = int(max(0, x1)), int(max(0, y1)); x2, y2 = int(min(img_w, x2)), int(min(img_h, y2))
        sel_w, sel_h = x2 - x1, y2 - y1
        if sel_w < MIN_SELECTION_SIZE or sel_h < MIN_SELECTION_SIZE:
            self._hide_crop_visuals()
            if hasattr(self, 'recrop_button'): self.recrop_button.configure(state="disabled")
        else:
            self.overlay_top.place(x=0, y=0, width=img_w, height=y1)
            self.overlay_bottom.place(x=0, y=y2, width=img_w, height=img_h - y2)
            self.overlay_left.place(x=0, y=y1, width=x1, height=sel_h)
            self.overlay_right.place(x=x2, y=y1, width=img_w - x2, height=sel_h)
            for ov in [self.overlay_top, self.overlay_bottom, self.overlay_left, self.overlay_right]:
                if ov.winfo_exists(): ov.lift()
            self.selection_rect_visual.configure(width=sel_w, height=sel_h) # type: ignore
            self.selection_rect_visual.place(x=x1, y=y1)
            if self.selection_rect_visual.winfo_exists(): self.selection_rect_visual.lift()
            hs = HANDLE_SIZE // 2
            handle_positions_coords = {
                "TOP_LEFT": (x1 - hs, y1 - hs), "TOP_RIGHT": (x2 - hs, y1 - hs),
                "BOTTOM_LEFT": (x1 - hs, y2 - hs), "BOTTOM_RIGHT": (x2 - hs, y2 - hs),
                "MID_TOP": (x1 + sel_w // 2 - hs, y1 - hs), "MID_BOTTOM": (x1 + sel_w // 2 - hs, y2 - hs),
                "MID_LEFT": (x1 - hs, y1 + sel_h // 2 - hs), "MID_RIGHT": (x2 - hs, y1 + sel_h // 2 - hs)
            }
            for pos_key, (px, py) in handle_positions_coords.items():
                if pos_key in self.handles and self.handles[pos_key].winfo_exists():
                    self.handles[pos_key].place(x=px, y=py); self.handles[pos_key].lift()
            if hasattr(self, 'recrop_button'): self.recrop_button.configure(state="normal")
        self.crop_selection_coords = (x1, y1, x2, y2)

    def on_image_area_press(self, event):
        if not hasattr(self.screenshot_image_label, 'image') or self.screenshot_image_label.image is None or not self.displayed_ctk_image_size: return # type: ignore
        clicked_on_handle = False
        for handle_key, hw in self.handles.items():
            try:
                if hw.winfo_ismapped():
                    hx, hy = hw.winfo_x(), hw.winfo_y(); h_w, h_h = hw.winfo_width(), hw.winfo_height()
                    if hx <= event.x < hx + h_w and hy <= event.y < hy + h_h: clicked_on_handle = True; return
            except tkinter.TclError as e: print(f"Warning: TclError for handle {handle_key} in on_image_area_press: {e}"); continue
        self.active_drag_mode = "new_selection"; self.drag_start_mouse_pos_relative_to_image = (event.x, event.y)
        self.crop_selection_coords = (event.x, event.y, event.x + 1, event.y + 1); self._update_crop_visuals()

    def on_image_area_drag(self, event):
        if self.active_drag_mode == "new_selection" and self.drag_start_mouse_pos_relative_to_image and self.displayed_ctk_image_size:
            img_w, img_h = self.displayed_ctk_image_size; sx, sy = self.drag_start_mouse_pos_relative_to_image
            cx = max(0, min(event.x, img_w -1)); cy = max(0, min(event.y, img_h -1))
            self.crop_selection_coords = (sx, sy, cx, cy)
            self._update_crop_visuals()

    def on_handle_press(self, event, handle_pos):
        if not self.crop_selection_coords or not self.displayed_ctk_image_size: return
        self.active_drag_mode = f"move_handle_{handle_pos}"; self.drag_start_selection_coords = self.crop_selection_coords
        self.drag_start_mouse_root_pos = (event.x_root, event.y_root)

    def on_handle_drag(self, event):
        if not self.active_drag_mode or not self.active_drag_mode.startswith("move_handle_") or not self.drag_start_selection_coords or not self.displayed_ctk_image_size or not self.drag_start_mouse_root_pos: return
        handle_type = self.active_drag_mode.split("move_handle_")[-1]; img_w, img_h = self.displayed_ctk_image_size
        try: label_root_x = self.screenshot_image_label.winfo_rootx(); label_root_y = self.screenshot_image_label.winfo_rooty()
        except tkinter.TclError: return
        current_mouse_x_on_label = max(0, min(event.x_root - label_root_x, img_w - 1))
        current_mouse_y_on_label = max(0, min(event.y_root - label_root_y, img_h - 1))
        s_x1, s_y1, s_x2, s_y2 = self.drag_start_selection_coords; new_x1, new_y1, new_x2, new_y2 = s_x1, s_y1, s_x2, s_y2
        if "LEFT" in handle_type: new_x1 = current_mouse_x_on_label
        elif "RIGHT" in handle_type: new_x2 = current_mouse_x_on_label
        if "TOP" in handle_type: new_y1 = current_mouse_y_on_label
        elif "BOTTOM" in handle_type: new_y2 = current_mouse_y_on_label
        if handle_type == "MID_TOP" or handle_type == "MID_BOTTOM": new_x1, new_x2 = s_x1, s_x2
        elif handle_type == "MID_LEFT" or handle_type == "MID_RIGHT": new_y1, new_y2 = s_y1, s_y2
        self.crop_selection_coords = (new_x1, new_y1, new_x2, new_y2); self._update_crop_visuals()

    def on_mouse_release_any(self, event):
        if self.active_drag_mode:
            if self.crop_selection_coords:
                r_x1, r_y1, r_x2, r_y2 = self.crop_selection_coords
                final_x1,final_y1 = min(r_x1,r_x2),min(r_y1,r_y2); final_x2,final_y2 = max(r_x1,r_x2),max(r_y1,r_y2)
                self.crop_selection_coords = (final_x1, final_y1, final_x2, final_y2); self._update_crop_visuals()
            if hasattr(self, 'recrop_button') and self.recrop_button.cget("state") == "disabled" and self.active_drag_mode == "new_selection": print("Selection too small or invalid on release.")
        self.active_drag_mode = None; self.drag_start_mouse_pos_relative_to_image = None; self.drag_start_selection_coords = None; self.drag_start_mouse_root_pos = None

    def trigger_recrop(self):
        if not self.original_pil_image_for_crop or not self.crop_selection_coords or not self.displayed_ctk_image_size: print("ERROR: Missing data for re-crop."); return
        sel_x1,sel_y1,sel_x2,sel_y2 = self.crop_selection_coords
        orig_w,orig_h=self.original_pil_image_for_crop.size; disp_w,disp_h=self.displayed_ctk_image_size
        if disp_w<=0 or disp_h<=0: print("ERROR: Displayed image has zero dimension."); return
        sc_x=orig_w/disp_w; sc_y=orig_h/disp_h; cx1,cy1=int(sel_x1*sc_x),int(sel_y1*sc_y); cx2,cy2=int(sel_x2*sc_x),int(sel_y2*sc_y)
        final_cx1=max(0,min(cx1,orig_w)); final_cy1=max(0,min(cy1,orig_h)); final_cx2=max(0,min(cx2,orig_w)); final_cy2=max(0,min(cy2,orig_h))
        if final_cx1 >= final_cx2 or final_cy1 >= final_cy2: print(f"ERROR: Invalid Pillow crop dims: ({final_cx1},{final_cy1},{final_cx2},{final_cy2})"); return
        try:
            cropped_img=self.original_pil_image_for_crop.crop((final_cx1,final_cy1,final_cx2,final_cy2)); self.original_pil_image_for_crop=cropped_img.copy()
            if self.current_image_path and "_recropped_temp" not in self.current_image_path and "_capture" not in self.current_image_path: base, ext = os.path.splitext(self.current_image_path); self.current_image_path = f"{base}_recropped_temp{ext}"
            elif not self.current_image_path : self.current_image_path = "recropped_image_from_unknown_source.png"
            self.original_pil_image_for_crop.save(self.current_image_path); print(f"Re-cropped: {self.current_image_path}, New Size: {self.original_pil_image_for_crop.size}");
            self._update_screenshot_display(self.original_pil_image_for_crop); self._update_answer_textbox(f"Re-cropped. New dims: {self.original_pil_image_for_crop.size}",False)
        except Exception as e: print(f"Error re-crop/display: {e}"); traceback.print_exc(); self._update_answer_textbox(f"Error during re-crop: {e}",False)

    def start_capture_thread(self):
        self.capture_button.configure(state="disabled", text="Capturing..."); self._update_screenshot_display(None)
        self.progress_dots.set_step(0)  # Reset to step 1
        self.current_dropdown_data = []; self._clear_answers(); self._update_answer_textbox("Waiting for screenshot...", placeholder=True)
        threading.Thread(target=self._run_capture_task_in_thread, args=(run_brave_screenshot_task,)).start()

    def _run_capture_task_in_thread(self, task_function):
        capture_result_data = None
        try:
            capture_result_data = task_function()
            screenshot_path = None; error_from_capture = None
            if isinstance(capture_result_data, dict): screenshot_path = capture_result_data.get("screenshot_path"); error_from_capture = capture_result_data.get("error")
            if screenshot_path and os.path.exists(screenshot_path):
                pil_image_result = Image.open(screenshot_path); self.current_image_path = os.path.abspath(screenshot_path); self.original_pil_image_for_crop = pil_image_result.copy()
                self.current_dropdown_data = capture_result_data.get("dropdowns_data", []); self.after(0, self._update_screenshot_display, pil_image_result)
                self.after(0, self._update_answer_textbox, f"Screenshot: {os.path.basename(screenshot_path)}", False)
                if self.current_dropdown_data: print(f"Extracted {len(self.current_dropdown_data)} dropdowns.")
                elif error_from_capture and "iframe" in error_from_capture.lower() and "not found" in error_from_capture.lower(): print("Note: Target iframe for dropdowns was not found.")
                else: print("No dropdowns extracted or iframe not targeted.")
            else:
                final_error_message = "Screenshot capture failed."
                if error_from_capture: final_error_message += f" Reason: {error_from_capture}"
                elif isinstance(capture_result_data, dict) and not screenshot_path: final_error_message += " (No screenshot path returned)."
                elif screenshot_path and not os.path.exists(screenshot_path): final_error_message += f" (Path '{screenshot_path}' does not exist)."
                else: final_error_message += " (Task returned unexpected data or None)."
                self.after(0, self._update_screenshot_display, None, final_error_message); self.current_image_path=None; self.original_pil_image_for_crop=None; self.current_dropdown_data=[]
        except Exception as e: print(f"Error in capture task thread: {e}\n"); traceback.print_exc(); self.after(0, self._update_screenshot_display, None, f"Capture error: {e}"); self.current_image_path=None; self.original_pil_image_for_crop=None; self.current_dropdown_data=[]
        finally: self.after(0, lambda: self.capture_button.configure(state="normal", text="Capture Question"))

    def _update_screenshot_display(self, pil_image_to_display: Image.Image = None, message: str = None): # type: ignore
        try:
            # CRITICAL: Clear all previous answers when loading new screenshot
            self._clear_answers()

            # CRITICAL: Clear cached base64 to prevent using old image data
            self.current_image_base64 = None
            self.current_image_base64_path = None
            print("🔄 New screenshot loaded - previous answers and cached data cleared")

            self._create_screenshot_image_label_with_children()
            if message: self.screenshot_image_label.configure(text=message, image=None); self.screenshot_image_label.image = None; self.displayed_ctk_image_size = None; self._hide_crop_visuals(); self.ai_button.configure(state="disabled"); return # type: ignore
            if pil_image_to_display is None: self.screenshot_image_label.configure(text="Processing...", image=None); self.screenshot_image_label.image = None; self.displayed_ctk_image_size = None; self._hide_crop_visuals(); self.ai_button.configure(state="disabled"); return # type: ignore
            self.screenshot_display_frame.update_idletasks(); container_width = self.screenshot_display_frame.winfo_width(); container_height = self.screenshot_display_frame.winfo_height()
            if container_width <= 10: container_width = 600
            if container_height <= 10: container_height = 450
            img_w, img_h = pil_image_to_display.size
            if img_w == 0 or img_h == 0: self.screenshot_image_label.configure(text="Invalid image (0 size)", image=None); self.screenshot_image_label.image = None; self.displayed_ctk_image_size = None; self._hide_crop_visuals(); self.ai_button.configure(state="disabled"); return # type: ignore
            aspect = img_w / img_h; disp_w = container_width; disp_h = int(disp_w / aspect)
            if disp_h > container_height: disp_h = container_height; disp_w = int(disp_h * aspect)
            disp_w, disp_h = max(1, int(disp_w)), max(1, int(disp_h)); self.displayed_ctk_image_size = (disp_w, disp_h)
            resized_img = pil_image_to_display.resize(self.displayed_ctk_image_size, Image.Resampling.LANCZOS); new_ctk_image = ctk.CTkImage(light_image=resized_img, dark_image=resized_img, size=self.displayed_ctk_image_size)
            self.screenshot_image_label.configure(image=new_ctk_image, text=""); self.screenshot_image_label.image = new_ctk_image; self._hide_crop_visuals() # type: ignore
            if self.current_image_path and os.path.exists(self.current_image_path) and self.screenshot_image_label.image is not None: self.ai_button.configure(state="normal"); self.progress_dots.set_step(1) # type: ignore
            else: self.ai_button.configure(state="disabled")
        except tkinter.TclError as tcl_err: print(f"TCL Error: {tcl_err}\n"); traceback.print_exc();
        except Exception as e: print(f"General Error in _update_screenshot_display: {e}\n"); traceback.print_exc();

    def _clear_answers(self):
        """Clear ALL answer display state including progressive containers"""
        # Destroy all widgets in answer frame
        for widget in self.answer_scroll_frame.winfo_children():
            widget.destroy()
        
        # Reset progressive state
        if hasattr(self, 'progressive_parser'):
            self.progressive_parser = None
        if hasattr(self, 'streaming_container'):
            self.streaming_container = None
        if hasattr(self, 'progressive_answers_container'):
            self.progressive_answers_container = None
        if hasattr(self, 'progressive_visual_grid'):
            self.progressive_visual_grid = None
        if hasattr(self, 'skeleton_frames'):
            self.skeleton_frames.clear()
        self.progressive_boxes_rendered = 0
        
        # Reset streaming state
        self.streaming_active = False
        self.accumulated_response = ""
        
        print("🧹 Answer display and state cleared")

    def _auto_scroll_to_answers(self):
        """Auto-scroll to bottom of answers container to show AI-generated answers"""
        try:
            if hasattr(self, 'answer_scroll_frame') and self.answer_scroll_frame.winfo_exists():
                # Update layout to ensure proper sizing
                self.answer_scroll_frame.update_idletasks()
                # Access internal canvas (CTkScrollableFrame wraps a canvas)
                if hasattr(self.answer_scroll_frame, '_parent_canvas'):
                    canvas = self.answer_scroll_frame._parent_canvas
                    canvas.yview_moveto(1.0)
                    print("📜 Auto-scrolled to answers")
        except Exception as e:
            print(f"⚠️ Auto-scroll error: {e}")

    def _debounced_scroll(self):
        """Debounced scroll handler for streaming updates"""
        self._scroll_pending = False
        self._auto_scroll_to_answers()

    def _update_answer_textbox(self, text_content, placeholder=True):
        self._clear_answers(); self.answer_scroll_frame.update_idletasks(); frame_width = self.answer_scroll_frame.winfo_width(); wraplen = max(200, frame_width - 40)
        placeholder_color = ("gray60", "gray40") if placeholder else None; msg_widget = ctk.CTkLabel(self.answer_scroll_frame, text=text_content, text_color=placeholder_color, wraplength=wraplen, justify="left"); msg_widget.grid(row=0, column=0, padx=10, pady=10, sticky="new")

    def _extract_option_letter(self, answer_id: str) -> str:
        """Extract A, B, C, D from answer IDs like 'mc_option_A', 'option_B', etc."""
        if not answer_id:
            return ""

        # Try to find a pattern like option_A, mc_option_B, etc.
        match = re.search(r'[_-]([A-D])(?:[_-]|$)', answer_id, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Fall back to just the last character if it's a letter
        if len(answer_id) > 0 and answer_id[-1].isalpha():
            return answer_id[-1].upper()

        return answer_id  # Return full ID if extraction fails

    def _process_ai_text_content(self, text: Union[str, None]) -> Union[str, None]:
        """Replaces '【None】' or 'None' with random numbers in AI-generated text."""
        if text is None:
            return None

        # Handle "【None】%" and "【None】"
        def replace_none_placeholder(match_obj):
            if match_obj.group(1) == "%":  # If % was present after 【None】
                return f"【{random.randint(1, 99)}】%"
            else:  # If just 【None】
                return f"【{random.randint(1, 10)}】" # Default random number for non-percentage

        processed_text = re.sub(r"【None】(%)?", replace_none_placeholder, text)

        # If the entire text was the literal string "None"
        if processed_text == "None":
            return str(random.randint(1, 10)) # Or a more context-appropriate random number
        
        return processed_text

    def _process_ai_response_data(self, response_data: dict) -> dict:
        """Processes the entire AI response to replace 'None' values."""
        if not response_data:
            return {} # Return empty dict if input is None or empty

        # Process identified_question
        if "identified_question" in response_data and response_data["identified_question"] is not None:
            response_data["identified_question"] = self._process_ai_text_content(response_data["identified_question"])

        # Process answers
        if "answers" in response_data and isinstance(response_data["answers"], list):
            processed_answers = []
            for ans_item in response_data["answers"]:
                if isinstance(ans_item, dict): # Ensure ans_item is a dictionary
                    if "text_content" in ans_item and ans_item["text_content"] is not None:
                        ans_item["text_content"] = self._process_ai_text_content(ans_item["text_content"])
                    
                    if "explanation" in ans_item and ans_item["explanation"] is not None:
                        ans_item["explanation"] = self._process_ai_text_content(ans_item["explanation"])

                    if ans_item.get("content_type") == "matching_pair" and "pair_data" in ans_item and isinstance(ans_item["pair_data"], dict):
                        if "term" in ans_item["pair_data"] and ans_item["pair_data"]["term"] is not None:
                            ans_item["pair_data"]["term"] = self._process_ai_text_content(ans_item["pair_data"]["term"])
                        if "match" in ans_item["pair_data"] and ans_item["pair_data"]["match"] is not None:
                            ans_item["pair_data"]["match"] = self._process_ai_text_content(ans_item["pair_data"]["match"])
                    
                    if ans_item.get("content_type") == "dropdown_choice" and "dropdown_selection_data" in ans_item and isinstance(ans_item["dropdown_selection_data"], dict):
                        if "selected_text" in ans_item["dropdown_selection_data"] and ans_item["dropdown_selection_data"]["selected_text"] is not None:
                            ans_item["dropdown_selection_data"]["selected_text"] = self._process_ai_text_content(ans_item["dropdown_selection_data"]["selected_text"])

                    if ans_item.get("content_type") == "ordered_sequence" and \
                       "sequence_data" in ans_item and isinstance(ans_item["sequence_data"], dict) and \
                       "items" in ans_item["sequence_data"] and isinstance(ans_item["sequence_data"]["items"], list):
                        ans_item["sequence_data"]["items"] = [self._process_ai_text_content(item) for item in ans_item["sequence_data"]["items"] if item is not None]
                    
                    if ans_item.get("content_type") == "table_completion" and \
                       "table_data" in ans_item and isinstance(ans_item["table_data"], dict) and \
                       "rows" in ans_item["table_data"] and isinstance(ans_item["table_data"]["rows"], list):
                        for row in ans_item["table_data"]["rows"]:
                            if isinstance(row, dict) and "row_cells" in row and isinstance(row["row_cells"], list):
                                for cell in row["row_cells"]:
                                    if isinstance(cell, dict) and "value" in cell and cell["value"] is not None:
                                        cell["value"] = self._process_ai_text_content(cell["value"])
                processed_answers.append(ans_item)
            response_data["answers"] = processed_answers
        
        return response_data

    def display_ai_answers(self, response_data):
        self._clear_answers()
        self.answer_scroll_frame.update_idletasks()
        equation_rendered_specially = False # Flag to track if special equation rendering happened
        
        # STRICT visual enhancement check - only for TRUE drag-to-image questions
        if VISUAL_ENHANCEMENT_AVAILABLE and self.visual_enhancement_enabled.get() and self.current_image_path and response_data:
            all_ans = response_data.get("answers", [])
            matching_pairs = [a for a in all_ans if a.get("content_type") == "matching_pair"]
            identified_q = response_data.get("identified_question", "").lower()
            
            # VERY STRICT criteria for visual enhancement:
            # Must explicitly mention dragging TO images/visual aids
            is_truly_visual = (
                len(matching_pairs) >= 4 and  # Require 4+ matches (not just 3)
                ("tile to the correct location on the image" in identified_q or
                 "drag each tile to the correct location" in identified_q or
                 "match the correct description with each visual aid" in identified_q)
            )
            
            # ALSO require visual terms in the pair data
            if is_truly_visual and matching_pairs:
                pair_terms = [p.get("pair_data", {}).get("term", "").lower() for p in matching_pairs]
                # Must have explicit visual descriptions
                visual_keywords = ["chart", "map", "building", "diagram", "graph", "pie"]
                visual_term_count = sum(1 for term in pair_terms if any(vk in term for vk in visual_keywords))
                
                # Require at least 3 matches to have visual terms
                if visual_term_count >= 3:
                    print(f"✅ Confirmed drag-to-image: {visual_term_count}/6 visual terms found")
                    try:
                        renderer = DragToImageRenderer(self.answer_scroll_frame, self.current_image_path)
                        visual_display = renderer.create_visual_matching_display(matching_pairs)
                        visual_display.pack(fill="both", expand=True)
                        return
                    except Exception as e:
                        print(f"⚠️ Visual display failed, using standard: {e}")
                        traceback.print_exc()
                else:
                    print(f"❌ Text-based matching ({visual_term_count}/6 visual terms) - standard display")
            else:
                print(f"❌ Not drag-to-image question - standard display")

        if not response_data or ("status" in response_data and response_data.get("status") != "SUCCESS" and response_data.get("status") != "PARTIAL_SUCCESS"):
            error_msg = "Error: Could not process request."

            # Special handling for rate limit errors
            if response_data and response_data.get("status") == "ERROR_RATE_LIMITED":
                cooldown = response_data.get("cooldown_seconds", 60)
                error_msg = (
                    f"⚠️ RATE LIMIT REACHED\n\n"
                    f"OpenRouter API rate limit exceeded.\n\n"
                    f"You have two options:\n\n"
                    f"1️⃣  Wait {cooldown} seconds and try again\n"
                    f"    (The API will be available after the cooldown period)\n\n"
                    f"2️⃣  Switch to a different model\n"
                    f"    (Use the AI Model dropdown in Settings)\n\n"
                    f"Cooldown period: {cooldown} seconds"
                )
            # Special handling for model not found (404)
            elif response_data and response_data.get("status") == "ERROR_MODEL_NOT_FOUND":
                error_msg = (
                    f"❌ MODEL NOT FOUND\n\n"
                    f"The selected model no longer exists on OpenRouter.\n\n"
                    f"Please select a different model from the dropdown in Settings."
                )
            # Generic error handling
            elif response_data and response_data.get("error_message"):
                error_msg = f"Error: {response_data['error_message']}"
            elif response_data and not response_data.get("answers") and response_data.get("identified_question"):
                error_msg = f"Identified Question: {response_data['identified_question']}\n\nNo specific answers provided by AI."
            elif not response_data:
                error_msg = "Error: No response data from AI."

            self._update_answer_textbox(error_msg, False); return

        content_container = ctk.CTkFrame(self.answer_scroll_frame, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=0, pady=0) # Use fill="both"
        
        identified_question_str = response_data.get("identified_question", "")
        all_ans = response_data.get("answers", [])
        answers_map = {ans.get("answer_id"): str(ans.get("text_content", "N/A")) # Default to N/A
                       for ans in all_ans
                       if isinstance(ans, dict) and ans.get("content_type") == "direct_answer" and ans.get("answer_id")}

        # --- Special Equation Rendering Logic ---
        equation_prefix_signal = "EQUATION_FORMULA::"
        if identified_question_str.startswith(equation_prefix_signal):
            equation_template = identified_question_str[len(equation_prefix_signal):].strip()
            # Regex to find placeholders like {{placeholder_name}}
            placeholders = re.findall(r"\{\{(.*?)\}\}", equation_template)
            
            # Try to match the specific visual structure: val1 ± val2 / √(val3)
            # Example template: "{{mean}} ± {{numerator}} / √({{denominator_n}})"
            equation_structure_match = re.match(r"\{\{(.*?)\}\}\s*±\s*\{\{(.*?)\}\}\s*/\s*√\(\s*\{\{(.*?)\}\}\s*\)", equation_template, re.IGNORECASE)

            if equation_structure_match and len(placeholders) == 3:
                p1_id, p2_id, p3_id = placeholders[0], placeholders[1], placeholders[2]
                
                val1 = answers_map.get(p1_id, f"{{{p1_id}}}")
                val2 = answers_map.get(p2_id, f"{{{p2_id}}}")
                val3 = answers_map.get(p3_id, f"{{{p3_id}}}")

                # Overall frame for the equation components
                eq_display_frame = ctk.CTkFrame(content_container, fg_color=("gray90", "gray20"), corner_radius=6)
                eq_display_frame.pack(pady=10, padx=10, fill="x")
                
                ctk.CTkLabel(eq_display_frame, text="Completed Equation:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,5))

                # Frame to hold the visual equation using grid
                eq_grid_frame = ctk.CTkFrame(eq_display_frame, fg_color="transparent")
                eq_grid_frame.pack(pady=5, padx=10, anchor="center")

                box_font = ctk.CTkFont(family="Segoe UI", size=14) # Normal weight for values
                operator_font = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
                box_fg_color = ("#F0F0F0", "#2B2B2B") 
                box_border_color = ("#B0B0B0", "#4B4B4B")
                box_width = 70
                box_height = 35
                box_corner_radius = 4

                # Helper to create styled box for values
                def create_value_box(parent, text_value):
                    frame = ctk.CTkFrame(parent, width=box_width, height=box_height, 
                                         fg_color=box_fg_color, border_color=box_border_color, 
                                         border_width=1, corner_radius=box_corner_radius)
                    frame.pack_propagate(False)
                    label = ctk.CTkLabel(frame, text=text_value, font=box_font)
                    label.pack(expand=True, padx=5, pady=5)
                    return frame

                # Layout:  [val1]  ±   [val2]
                #                     ------
                #                    √([val3])

                # Term 1 (val1)
                term1_box = create_value_box(eq_grid_frame, val1)
                term1_box.grid(row=0, column=0, rowspan=3, padx=(0, 10), sticky="nsew") # Span rows to align with fraction

                # ± operator
                plus_minus_label = ctk.CTkLabel(eq_grid_frame, text="±", font=operator_font)
                plus_minus_label.grid(row=0, column=1, rowspan=3, padx=10, sticky="nsew")

                # Numerator (val2)
                num_box = create_value_box(eq_grid_frame, val2)
                num_box.grid(row=0, column=2, pady=(0,2), sticky="s") # sticky south for alignment

                # Fraction Bar
                bar_frame = ctk.CTkFrame(eq_grid_frame, height=2, fg_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
                bar_frame.grid(row=1, column=2, sticky="ew", padx=5)
                
                # Denominator part: √ ( val3 )
                den_outer_frame = ctk.CTkFrame(eq_grid_frame, fg_color="transparent")
                den_outer_frame.grid(row=2, column=2, pady=(2,0), sticky="n") # sticky north

                sqrt_label = ctk.CTkLabel(den_outer_frame, text="√(", font=operator_font)
                sqrt_label.pack(side="left", anchor="center")
                
                den_val_box = create_value_box(den_outer_frame, val3)
                den_val_box.pack(side="left", padx=(0,2))

                close_paren_label = ctk.CTkLabel(den_outer_frame, text=")", font=operator_font)
                close_paren_label.pack(side="left", anchor="center")
                
                equation_rendered_specially = True
            else: # If EQUATION_FORMULA prefix but not the specific structure, show the template and then answers
                ctk.CTkLabel(content_container, text="Equation Template:", font=ctk.CTkFont(weight="bold")).pack(pady=(5,2), padx=10, anchor="w")
                q_text_w = ctk.CTkTextbox(content_container, wrap="word", fg_color=("gray90", "gray20"), activate_scrollbars=False, border_width=0, corner_radius=4)
                q_text_w.insert("1.0", equation_template)
                q_text_w.update_idletasks()
                num_l_q = equation_template.count('\n') + 1 + len(equation_template) // ( (q_text_w.winfo_width()//7) if q_text_w.winfo_width() > 20 else 50 )
                h_q = max(20, num_l_q * 18 + 10)
                q_text_w.configure(state="disabled", height=h_q)
                q_text_w.pack(pady=(0,10),padx=10,fill="x",expand=True)
        
        # --- Fallback / Standard Identified Question Display (if not special equation) ---
        if not equation_rendered_specially and identified_question_str:
            reconstructed_question_text = identified_question_str # Start with original
            # Perform standard placeholder substitution if not done by special equation
            if answers_map and "{{" in identified_question_str:
                temp_reconstructed_text = identified_question_str
                sorted_answer_ids_for_substitution = sorted(answers_map.keys(), key=len, reverse=True)
                for answer_id in sorted_answer_ids_for_substitution:
                    placeholder = f"{{{{{answer_id}}}}}"
                    if placeholder in temp_reconstructed_text:
                        answer_value = answers_map[answer_id]
                        styled_answer = f"【{answer_value}】" 
                        temp_reconstructed_text = temp_reconstructed_text.replace(placeholder, styled_answer, 1) 
                reconstructed_question_text = temp_reconstructed_text

            q_frame = ctk.CTkFrame(content_container, fg_color=("gray90", "gray20"), corner_radius=6)
            q_frame.pack(fill="x", padx=5, pady=(5,10), expand=True);
            ctk.CTkLabel(q_frame, text="Identified Question / Context:", font=ctk.CTkFont(weight="bold")).pack(pady=(5,2), padx=10, anchor="w")
            q_text_w = ctk.CTkTextbox(q_frame, wrap="word", fg_color="transparent", activate_scrollbars=False, border_width=0)
            q_text_w.insert("1.0", reconstructed_question_text if reconstructed_question_text else "N/A")
            q_frame.update_idletasks(); q_text_w.update_idletasks()
            q_text_content_actual = q_text_w.get("1.0", "end-1c")
            num_l_q = q_text_content_actual.count('\n') + 1
            q_text_widget_width = q_text_w.winfo_width()
            if q_text_widget_width > 20 : 
                chars_per_line = q_text_widget_width // 7 
                if chars_per_line > 0: num_l_q += len(q_text_content_actual) // chars_per_line
            h_q = max(20, num_l_q * 18 + 10)
            q_text_w.configure(state="disabled",height=h_q)
            q_text_w.pack(pady=(0,5),padx=10,fill="x",expand=True)

            # Auto-scroll to answers if question is very tall
            q_frame.update_idletasks()
            question_frame_height = q_frame.winfo_height()
            if question_frame_height > 300:
                # Schedule scroll after a brief delay to ensure all widgets are rendered
                def scroll_to_answers():
                    if hasattr(self.answer_scroll_frame, '_parent_canvas'):
                        canvas = self.answer_scroll_frame._parent_canvas
                        canvas.yview_moveto(0.35)
                self.after(150, scroll_to_answers)
                print(f"📜 Auto-scrolled to answers section (question height: {question_frame_height}px)")

        # --- Detect Dropdown-Only Fill-in-the-Blank Questions ---
        is_dropdown_only_question = False
        if identified_question_str and "{{" in identified_question_str and all_ans:
            # Count dropdown answers
            dropdown_count = sum(1 for ans in all_ans if isinstance(ans, dict) and ans.get("content_type") == "dropdown_choice")
            total_answers = len([ans for ans in all_ans if isinstance(ans, dict)])

            # If 80%+ answers are dropdowns and we have placeholders, it's a dropdown-only question
            if total_answers > 0 and dropdown_count >= total_answers * 0.8:
                is_dropdown_only_question = True
                print(f"📝 Dropdown-only question detected ({dropdown_count}/{total_answers} dropdowns)")

                # Add visual note that answers are filled in above
                note_frame = ctk.CTkFrame(content_container, fg_color=("gray85", "gray22"), corner_radius=6)
                note_frame.pack(fill="x", padx=5, pady=(0, 10))
                note_label = ctk.CTkLabel(
                    note_frame,
                    text="✓ Answers filled in the paragraph above (highlighted in 【brackets】)",
                    font=ctk.CTkFont(size=11, slant="italic"),
                    text_color=("#2E7D32", "#4CAF50")
                )
                note_label.pack(pady=6, padx=10)

        # --- Displaying Individual Answer Items ---
        if not all_ans and not identified_question_str and not equation_rendered_specially:
             ctk.CTkLabel(content_container, text="AI provided no information.", text_color=("gray60","gray40")).pack(pady=10)
             return
        elif not all_ans and equation_rendered_specially: # Equation was shown, no other items
            return
        elif not all_ans: # Question might have been shown, but no answer items
            print("ℹ️ No detailed answer items to display.")
            return

        detailed_answers_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        detailed_answers_frame.pack(fill="x", expand=True, padx=0, pady=(5,0))
        display_item_count = 0
        
        valid_ans_items = [ans for ans in all_ans if isinstance(ans, dict)]
        sorted_ans = sorted(valid_ans_items, key=lambda x: (
            x.get("is_correct_option", False) is False, 
            # If equation was rendered, de-prioritize its individual components unless they have explanations
            equation_rendered_specially and x.get("answer_id") in answers_map and x.get("answer_id") in identified_question_str and not x.get("explanation"),
            {"table_completion": 0, "ordered_sequence": 1, "matching_pair": 2, "dropdown_choice": 3, "multiple_choice_option": 4, "direct_answer": 5, "text_plain": 6}.get(x.get("content_type","text_plain"), 99)
        ))

        for i, ans_item in enumerate(sorted_ans):
            show_detailed_item = True
            ans_item_id = ans_item.get("answer_id")
            c_type = ans_item.get("content_type", "text_plain")

            if equation_rendered_specially and ans_item_id in answers_map and ans_item_id in identified_question_str and not ans_item.get("explanation"):
                show_detailed_item = False # Don't show if part of special equation and no extra explanation

            # Skip dropdown cards if they're already shown in the filled paragraph
            if is_dropdown_only_question and c_type == "dropdown_choice":
                if answers_map and ans_item_id in answers_map:
                    # This dropdown was already filled in the paragraph above
                    show_detailed_item = False
                    print(f"   ⏭️  Skipping redundant dropdown card: {ans_item_id}")

            if not show_detailed_item:
                continue

            # ... (rest of the existing answer item display logic: multiple_choice, matching_pair, etc.) ...
            # This part remains the same as your previous version, ensuring it handles all other content_types.
            # For brevity, I'm not repeating that large block here, but it should be included from your previous version.
            # Ensure that this section correctly uses `ans_item.get("text_content")` which is already processed.

            display_item_count +=1
            # c_type already defined above for early filtering
            conf=ans_item.get("confidence"); conf_s=f"(Confidence: {conf*100:.0f}%)" if conf is not None else ""; is_corr=ans_item.get("is_correct_option",False)
            
            base_fg_color = ("gray80", "gray25"); base_border_color = ("gray70", "gray30"); title_font_weight = "normal"; title_slant = "italic"
            item_prefix = ""

            if is_corr: 
                base_fg_color = ("#e8f5e9","#1a311a"); base_border_color = ("#4CAF50","#388E3C"); title_font_weight = "bold"; title_slant = "roman"
                if c_type == "multiple_choice_option": item_prefix = "✅ " 
            
            if c_type == "matching_pair": base_fg_color=("#e8f0fe","#1c2333"); base_border_color=("#4a90e2","#2a5298"); title_slant="roman"
            elif c_type == "table_completion": base_fg_color=("#fff0e6", "#331a00"); base_border_color=("#FF8C00","#B22222"); title_slant="roman"
            elif c_type == "ordered_sequence": base_fg_color=("#e0f7f4", "#142e2a"); base_border_color=("#1ABC9C","#16A085"); title_slant="roman"
            elif c_type == "dropdown_choice": base_fg_color=("#f4eef7","#2c1b3e"); base_border_color=("#9b59b6","#7d3c98"); title_slant="roman"
            
            ans_item_frame = ctk.CTkFrame(detailed_answers_frame, fg_color=base_fg_color, border_color=base_border_color, border_width=1, corner_radius=6)
            ans_item_frame.pack(fill="x", padx=5, pady=(0, 8), expand=True)
            
            header_text = ""
            answer_content_text = str(ans_item.get("text_content", "")) 
            ans_id_from_item_header = ans_item.get("answer_id", f"Item {display_item_count if display_item_count > 0 else i+1}")

            if c_type == "direct_answer":
                header_text = f"Answer for '{ans_id_from_item_header}': {conf_s}"
                if is_corr: title_slant="roman" 
            elif c_type == "multiple_choice_option":
                # Badge-style display for multiple choice
                option_text_from_ai = answer_content_text if answer_content_text else "[Option Text Missing]"

                # Create horizontal badge frame
                badge_frame = ctk.CTkFrame(ans_item_frame, fg_color="transparent")
                badge_frame.pack(fill="x", padx=10, pady=8)

                # Extract option letter (A, B, C, D)
                option_letter = self._extract_option_letter(ans_id_from_item_header)

                # Option letter badge (large, prominent)
                letter_fg_color = ("#4CAF50", "#2E7D32") if is_corr else ("#2196F3", "#1565C0")
                letter_badge = ctk.CTkLabel(
                    badge_frame,
                    text=option_letter,
                    width=45,
                    height=45,
                    corner_radius=22,
                    fg_color=letter_fg_color,
                    font=ctk.CTkFont(size=22, weight="bold"),
                    text_color=("white", "white")
                )
                letter_badge.pack(side="left", padx=(0,12))

                # Option text
                text_label = ctk.CTkLabel(
                    badge_frame,
                    text=option_text_from_ai,
                    wraplength=450,
                    anchor="w",
                    justify="left",
                    font=ctk.CTkFont(size=13)
                )
                text_label.pack(side="left", fill="x", expand=True)

                # Confidence badge
                if conf is not None:
                    conf_percent = conf * 100
                    if conf >= 0.9:
                        conf_color = ("#4CAF50", "#2E7D32")  # Green for high confidence
                    elif conf >= 0.75:
                        conf_color = ("#FF9800", "#F57C00")  # Orange for medium
                    else:
                        conf_color = ("#FF5722", "#D84315")  # Red for low

                    conf_badge = ctk.CTkLabel(
                        badge_frame,
                        text=f"{conf_percent:.0f}%",
                        fg_color=conf_color,
                        corner_radius=12,
                        width=55,
                        height=28,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=("white", "white")
                    )
                    conf_badge.pack(side="right", padx=(12,0))

                # Clear header_text and answer_content since we rendered inline
                header_text = ""
                answer_content_text = "" 
            elif c_type == "matching_pair":
                pair_d = ans_item.get("pair_data", {}); 
                term = str(pair_d.get("term","N/A")); match_val = str(pair_d.get("match","N/A"))
                header_text = f"Match '{ans_id_from_item_header}': {conf_s}"; 
                answer_content_text = f"'{term}'  ➡️  '{match_val}'" 
            elif c_type == "dropdown_choice":
                dd_sel_d=ans_item.get("dropdown_selection_data",{});
                sel_t=str(dd_sel_d.get("selected_text","N/A"))
                dropdown_id_str = dd_sel_d.get('dropdown_id', ans_id_from_item_header)
                header_text = f"Dropdown ({dropdown_id_str}): {conf_s}"; 
                answer_content_text = f"Selected: '{sel_t}'"
            elif c_type == "table_completion":
                header_text = f"Table Completion '{ans_id_from_item_header}': {conf_s}"; answer_content_text = "" 
            elif c_type == "ordered_sequence":
                header_text = f"Ordered Sequence '{ans_id_from_item_header}': {conf_s}"; answer_content_text = ""
            elif c_type == "text_selection":
                # Extract image number from answer_id for display (e.g., "image_2" → "Image #2")
                import re
                img_match = re.search(r'image[_-]?(\d+)', ans_id_from_item_header, re.IGNORECASE)
                img_num = img_match.group(1) if img_match else "?"

                # Create badge-style display similar to multiple choice
                badge_frame = ctk.CTkFrame(ans_item_frame, fg_color="transparent")
                badge_frame.pack(fill="x", padx=10, pady=8)

                # Image reference badge
                img_badge = ctk.CTkLabel(
                    badge_frame,
                    text=f"#{img_num}",
                    width=45,
                    height=45,
                    corner_radius=22,
                    fg_color=("#9C27B0", "#6A1B9A"),  # Purple for image reference
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=("white", "white")
                )
                img_badge.pack(side="left", padx=(0,12))

                # Selected text content
                text_label = ctk.CTkLabel(
                    badge_frame,
                    text=answer_content_text,
                    wraplength=450,
                    anchor="w",
                    justify="left",
                    font=ctk.CTkFont(size=13)
                )
                text_label.pack(side="left", fill="x", expand=True)

                # Confidence badge
                if conf is not None:
                    conf_percent = conf * 100
                    if conf >= 0.9:
                        conf_color = ("#4CAF50", "#2E7D32")
                    elif conf >= 0.75:
                        conf_color = ("#FF9800", "#F57C00")
                    else:
                        conf_color = ("#FF5722", "#D84315")

                    conf_badge = ctk.CTkLabel(
                        badge_frame,
                        text=f"{conf_percent:.0f}%",
                        fg_color=conf_color,
                        corner_radius=12,
                        width=55,
                        height=28,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=("white", "white")
                    )
                    conf_badge.pack(side="right", padx=(12,0))

                # Clear header_text and answer_content since we rendered inline
                header_text = ""
                answer_content_text = ""
            else:
                 header_text = f"{c_type.replace('_', ' ').title()} ({ans_id_from_item_header}): {conf_s}"

            # Only render header if it's not empty (some types render inline)
            if header_text:
                ctk.CTkLabel(ans_item_frame, text=header_text, font=ctk.CTkFont(weight=title_font_weight, slant=title_slant), anchor="w", wraplength=self.answer_scroll_frame.winfo_width()-40).pack(fill="x", padx=10, pady=(5,2))

            if c_type == "table_completion" and isinstance(ans_item.get("table_data"), dict):
                table_data = ans_item.get("table_data", {})
                headers = table_data.get("headers", [])
                rows_data = table_data.get("rows", [])
                if headers and rows_data:
                    table_frame = ctk.CTkFrame(ans_item_frame, fg_color="transparent")
                    table_frame.pack(fill="x", padx=10, pady=5)
                    for col_idx, header_val in enumerate(headers): # Renamed header to header_val
                        ctk.CTkLabel(table_frame, text=str(header_val), font=ctk.CTkFont(weight="bold")).grid(row=0, column=col_idx, padx=5, pady=2, sticky="w")
                    for row_idx, row_item in enumerate(rows_data):
                        if isinstance(row_item, dict):
                            cells = row_item.get("row_cells", [])
                            for col_idx, cell in enumerate(cells):
                                if isinstance(cell, dict):
                                    cell_value = str(cell.get("value", "N/A")) 
                                    cell_label = ctk.CTkLabel(table_frame, text=cell_value)
                                    cell_label.grid(row=row_idx + 1, column=col_idx, padx=5, pady=2, sticky="w")
                                    if cell.get("is_ai_provided"):
                                        cell_label.configure(font=ctk.CTkFont(weight="bold")) 
            
            elif c_type == "ordered_sequence" and isinstance(ans_item.get("sequence_data"), dict):
                sequence_data = ans_item.get("sequence_data", {})
                items = sequence_data.get("items", []) 
                seq_prompt = sequence_data.get("prompt_text") 
                if seq_prompt:
                     ctk.CTkLabel(ans_item_frame, text=f"Task: {seq_prompt}", font=ctk.CTkFont(slant="italic")).pack(fill="x", padx=10, pady=(2,2))
                if items:
                    seq_text = "\n".join([f"{idx+1}. {str(item_val)}" for idx, item_val in enumerate(items)]) # Renamed item to item_val
                    seq_textbox = ctk.CTkTextbox(ans_item_frame, wrap="word", fg_color="transparent", activate_scrollbars=False, border_width=0)
                    seq_textbox.insert("1.0", seq_text)
                    seq_textbox.update_idletasks()
                    num_lines_seq = seq_text.count('\n') + 1
                    text_height_seq = max(1, num_lines_seq) * 18 + 10
                    seq_textbox.configure(state="disabled", height=text_height_seq)
                    seq_textbox.pack(fill="x", padx=10, pady=(0,5))

            elif answer_content_text: 
                content_textbox = ctk.CTkTextbox(ans_item_frame, wrap="word", fg_color="transparent", activate_scrollbars=False, border_width=0)
                content_textbox.insert("1.0", answer_content_text) 
                content_textbox.update_idletasks()
                num_lines = answer_content_text.count('\n') + 1
                text_height = max(1, num_lines) * 18 + 10 
                content_textbox.configure(state="disabled", height=text_height)
                content_textbox.pack(fill="x", padx=10, pady=(0,5))

            explanation = ans_item.get("explanation") 
            if explanation:
                ctk.CTkLabel(ans_item_frame, text="Explanation:", font=ctk.CTkFont(slant="italic", weight="bold"), anchor="w").pack(fill="x", padx=10, pady=(5,0))
                expl_textbox = ctk.CTkTextbox(ans_item_frame, wrap="word", fg_color=("gray88","gray22"), activate_scrollbars=False, border_width=0, corner_radius=4) 
                expl_textbox.insert("1.0", explanation)
                expl_textbox.update_idletasks()
                num_lines_expl = explanation.count('\n') + 1
                text_height_expl = max(1, num_lines_expl) * 18 + 10
                expl_textbox.configure(state="disabled", height=text_height_expl)
                expl_textbox.pack(fill="x", padx=10, pady=(0,5), expand=True)
        # End of loop for individual answer items

        if display_item_count == 0 and not identified_question_str and not equation_rendered_specially : 
             ctk.CTkLabel(content_container, text="AI provided no specific answer items to display.", text_color=("gray60","gray40")).pack(pady=10)
        elif display_item_count == 0 and (identified_question_str or equation_rendered_specially):
            # This means a question or equation was displayed, but no *additional* detailed answer items were suitable for display.
            print("ℹ️ Main question/equation displayed.")


    def start_ai_thread(self):
        if not self.current_image_path or not os.path.exists(self.current_image_path) or (hasattr(self.screenshot_image_label, 'image') and self.screenshot_image_label.image is None): self._update_answer_textbox("Please capture or re-crop a valid image first.", False); return # type: ignore
        api_key = self.api_key_var.get()
        selected_display_name = self.selected_model_var.get()
        # Convert display name to model ID for API call
        selected_model = self._get_model_id_from_display(selected_display_name)

        if not api_key: print("ERROR: API Key not set."); self._update_answer_textbox("Error: OpenRouter API Key not set. Please set it in Settings and save.", False); return
        if not selected_model or selected_model not in AVAILABLE_MODELS :
            current_default = DEFAULT_MODEL; print(f"ERROR: Selected model '{selected_model}' invalid. Defaulting to '{current_default}'")
            self._update_answer_textbox(f"Error: Selected model '{selected_model}' invalid. Choose suitable model.", False)
            if current_default and current_default in AVAILABLE_MODELS: self.selected_model_var.set(current_default); selected_model = current_default
            else: self.ai_button.configure(state="disabled", text="AI Model Invalid"); return
        # PHASE 1: Initialize progressive display
        self.ai_button.configure(state="disabled", text="⚡ Initializing...")
        self._clear_answers()

        # Initialize progressive parser
        if PROGRESSIVE_PARSER_AVAILABLE:
            self.progressive_parser = ProgressiveJSONParser()
        
        # Create main streaming container (formatted elements will appear here)
        self.streaming_container = ctk.CTkFrame(self.answer_scroll_frame, fg_color="transparent")
        self.streaming_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initial status label
        self.streaming_status_label = ctk.CTkLabel(
            self.streaming_container,
            text="🔄 Analyzing question...",
            font=("Segoe UI", 11, "italic"),
            text_color=("gray50", "gray60")
        )
        self.streaming_status_label.pack(pady=10)
        
        # Container for progressive answers
        self.progressive_answers_container = ctk.CTkFrame(self.streaming_container, fg_color="transparent")
        self.progressive_answers_container.pack(fill="both", expand=True)

        # Skeleton tracking for progressive loading
        self.skeleton_frames = {}  # Maps answer_id to skeleton frame widget

        # Reset analysis display flag for new request
        if hasattr(self, 'analysis_displayed'):
            delattr(self, 'analysis_displayed')

        
        base_prompt = """You are a helpful homework assistant. Analyze the question in the provided image.
Structure your response strictly according to the provided JSON schema.
For every answer item you provide, include a 'confidence' score (0.0-1.0).

**CRITICAL: INITIAL ANALYSIS AND METADATA FIRST FOR PROGRESSIVE RENDERING**
Your JSON response MUST begin with TWO fields in this exact order:
1. 'initial_analysis' field as the VERY FIRST field
2. 'metadata' field as the second field

This ordering is essential for creating proper UI display and loading placeholders while your answer streams in.

**INITIAL_ANALYSIS STRUCTURE:**
The 'initial_analysis' object must contain:

1. 'question_type': The detected question type (string) - one of the types listed below in metadata section

2. 'edmentum_type_name': A human-readable name for the Edmentum question type (string). Examples:
   - "Multiple Choice Question"
   - "Matched Pairs (Drag and Drop)"
   - "Dropdown/Cloze Question"
   - "Fill in the Blank"
   - "Hot Text (Text Selection)"
   - "Multi-Part Question"

3. 'placeholder_mapping': Array of objects mapping each placeholder in the question to its purpose. Each object has:
   - 'placeholder': The placeholder string (e.g., "{{answer_1}}", "{{dropdown_2}}")
   - 'type': The content_type for this placeholder (e.g., "multiple_choice_option", "dropdown_choice", "direct_answer")
   - 'label': Optional short label (e.g., "Option A", "Blank 1", "Part A")
   - 'purpose': Optional brief description of what this placeholder represents

4. 'visual_elements': Object describing visual elements detected in the image:
   - 'has_image': true/false - Contains photographs or illustrations
   - 'has_diagram': true/false - Contains diagrams or technical drawings
   - 'has_graph': true/false - Contains charts, graphs, or plots
   - 'has_table': true/false - Contains data tables or grids
   - 'interactive_elements': Array of strings describing interaction types (e.g., ["click_selection", "drag_drop", "text_input"])

5. 'rendering_strategy': String indicating how the UI should render this question. Must be one of:
   - "edmentum_multiple_choice" - Use when question_type is "multiple_choice" with 2-6 clearly labeled options
   - "edmentum_matching_pairs" - Use when question_type is "matching_pair" with 2+ term-definition pairs
   - "edmentum_dropdown" - Use when question_type is "dropdown_choice" with inline dropdown selections
   - "edmentum_fill_blank" - Use when question_type is "fill_in_blank" with text input fields
   - "edmentum_hot_text" - Use when question_type is "text_selection" with selectable text passages
   - "standard_fallback" - Use for any other question types or mixed formats

**INITIAL_ANALYSIS EXAMPLES:**

Multiple Choice Question:
```json
{
  "initial_analysis": {
    "question_type": "multiple_choice",
    "edmentum_type_name": "Multiple Choice Question",
    "placeholder_mapping": [],
    "visual_elements": {
      "has_image": false,
      "has_diagram": false,
      "has_graph": false,
      "has_table": false,
      "interactive_elements": ["click_selection"]
    },
    "rendering_strategy": "edmentum_multiple_choice"
  },
  "metadata": {...},
  "identified_question": "What is the main theme?",
  "answers": [...]
}
```

Matching Pairs:
```json
{
  "initial_analysis": {
    "question_type": "matching_pair",
    "edmentum_type_name": "Matched Pairs (Drag and Drop)",
    "placeholder_mapping": [],
    "visual_elements": {
      "has_image": false,
      "has_diagram": true,
      "has_graph": false,
      "has_table": false,
      "interactive_elements": ["drag_drop"]
    },
    "rendering_strategy": "edmentum_matching_pairs"
  },
  "metadata": {...},
  "identified_question": "Match each term to its definition",
  "answers": [...]
}
```

Dropdown Question:
```json
{
  "initial_analysis": {
    "question_type": "dropdown_choice",
    "edmentum_type_name": "Dropdown/Cloze Question",
    "placeholder_mapping": [
      {"placeholder": "{{dropdown_1}}", "type": "dropdown_choice", "label": "Blank 1", "purpose": "Verb tense"},
      {"placeholder": "{{dropdown_2}}", "type": "dropdown_choice", "label": "Blank 2", "purpose": "Subject"}
    ],
    "visual_elements": {
      "has_image": false,
      "has_diagram": false,
      "has_graph": false,
      "has_table": false,
      "interactive_elements": ["dropdown_selection"]
    },
    "rendering_strategy": "edmentum_dropdown"
  },
  "metadata": {...},
  "identified_question": "The sentence {{dropdown_1}} correctly {{dropdown_2}}.",
  "answers": [...]
}
```

Fill in the Blank:
```json
{
  "initial_analysis": {
    "question_type": "fill_in_blank",
    "edmentum_type_name": "Fill in the Blank",
    "placeholder_mapping": [
      {"placeholder": "{{answer_1}}", "type": "direct_answer", "label": "Blank 1"},
      {"placeholder": "{{answer_2}}", "type": "direct_answer", "label": "Blank 2"}
    ],
    "visual_elements": {
      "has_image": false,
      "has_diagram": false,
      "has_graph": true,
      "has_table": false,
      "interactive_elements": ["text_input"]
    },
    "rendering_strategy": "edmentum_fill_blank"
  },
  "metadata": {...},
  "identified_question": "The mean is {{answer_1}} and standard deviation is {{answer_2}}.",
  "answers": [...]
}
```

Hot Text (Text Selection):
```json
{
  "initial_analysis": {
    "question_type": "text_selection",
    "edmentum_type_name": "Hot Text (Text Selection)",
    "placeholder_mapping": [],
    "visual_elements": {
      "has_image": false,
      "has_diagram": false,
      "has_graph": false,
      "has_table": false,
      "interactive_elements": ["text_selection"]
    },
    "rendering_strategy": "edmentum_hot_text"
  },
  "metadata": {...},
  "identified_question": "Select the text passages that support the main argument.",
  "answers": [...]
}
```

**METADATA STRUCTURE (comes after initial_analysis):**

The metadata object must contain:
1. 'question_type': The primary type of question (string). Possible values:
   - "multiple_choice" - Radio button options (A, B, C, D)
   - "multiple_response" - Checkbox options (select all that apply)
   - "text_selection" - Click/select highlighted text passages
   - "matching_pair" - Match terms to definitions or drag tiles to targets
   - "dropdown_choice" - Fill-in-the-blank with dropdown menus
   - "fill_in_blank" - Type text into blank fields
   - "ordered_sequence" - Arrange items in correct order
   - "table_completion" - Fill cells in a table
   - "equation_formula" - Complete a mathematical equation with values
   - "constructed_response" - Essay or paragraph text box
   - "hot_spot" - Click a location on an image
   - "graphing" - Plot points on a coordinate grid
   - "number_line" - Plot on a number line
   - "freehand_drawing" - Draw on a canvas
   - "multi_part" - Question with multiple distinct sections (Part A, B, C)

2. 'total_answers': Total number of answer objects you will provide (integer)

3. 'answer_structure': Array describing each answer you will provide. Each element must have:
   - 'type': The content_type of this answer ("multiple_choice_option", "matching_pair", "dropdown_choice", "direct_answer", "text_selection", etc.)
   - 'id': The answer_id that will be used (e.g., "mc_option_A", "match_pair_1", "part_A_blank_1")
   - 'label': Optional display label (e.g., "A", "B", "Option 1", "Pair 1")

**METADATA EXAMPLES:**

Multiple Choice (4 options):
```json
{
  "metadata": {
    "question_type": "multiple_choice",
    "total_answers": 4,
    "answer_structure": [
      {"type": "multiple_choice_option", "id": "mc_option_A", "label": "A"},
      {"type": "multiple_choice_option", "id": "mc_option_B", "label": "B"},
      {"type": "multiple_choice_option", "id": "mc_option_C", "label": "C"},
      {"type": "multiple_choice_option", "id": "mc_option_D", "label": "D"}
    ]
  },
  "identified_question": "What is the main theme?",
  "answers": [...]
}
```

Matching Pairs (3 pairs):
```json
{
  "metadata": {
    "question_type": "matching_pair",
    "total_answers": 3,
    "answer_structure": [
      {"type": "matching_pair", "id": "match_pair_1", "label": "Pair 1"},
      {"type": "matching_pair", "id": "match_pair_2", "label": "Pair 2"},
      {"type": "matching_pair", "id": "match_pair_3", "label": "Pair 3"}
    ]
  },
  "identified_question": "Match each term to its definition",
  "answers": [...]
}
```

Text Selection (4 passages):
```json
{
  "metadata": {
    "question_type": "text_selection",
    "total_answers": 4,
    "answer_structure": [
      {"type": "text_selection", "id": "text_selection_1", "label": "#1"},
      {"type": "text_selection", "id": "text_selection_2", "label": "#2"},
      {"type": "text_selection", "id": "text_selection_3", "label": "#3"},
      {"type": "text_selection", "id": "text_selection_4", "label": "#4"}
    ]
  },
  "identified_question": "Select the lines that show...",
  "answers": [...]
}
```

Dropdown Fill-in-Blanks (3 dropdowns):
```json
{
  "metadata": {
    "question_type": "dropdown_choice",
    "total_answers": 3,
    "answer_structure": [
      {"type": "dropdown_choice", "id": "dropdown_1", "label": "Blank 1"},
      {"type": "dropdown_choice", "id": "dropdown_2", "label": "Blank 2"},
      {"type": "dropdown_choice", "id": "dropdown_3", "label": "Blank 3"}
    ]
  },
  "identified_question": "The sonnet is written in {{dropdown_1}} form...",
  "answers": [...]
}
```

Multi-Part Question (Part A has 2 blanks, Part B has 4 MC options):
```json
{
  "metadata": {
    "question_type": "multi_part",
    "total_answers": 6,
    "answer_structure": [
      {"type": "direct_answer", "id": "part_A_blank_1", "label": "Part A - Blank 1"},
      {"type": "direct_answer", "id": "part_A_blank_2", "label": "Part A - Blank 2"},
      {"type": "multiple_choice_option", "id": "part_B_mc_option_A", "label": "Part B - A"},
      {"type": "multiple_choice_option", "id": "part_B_mc_option_B", "label": "Part B - B"},
      {"type": "multiple_choice_option", "id": "part_B_mc_option_C", "label": "Part B - C"},
      {"type": "multiple_choice_option", "id": "part_B_mc_option_D", "label": "Part B - D"}
    ]
  },
  "identified_question": "Part A: The mean is {{part_A_blank_1}}... Part B: What is the difference?",
  "answers": [...]
}
```

**WHY THIS MATTERS:**
When you stream your response, the UI needs to know what type of answer placeholders to create BEFORE the actual answers arrive. The metadata allows the UI to show proper loading skeletons instead of raw JSON text. Always put metadata first!

IMPORTANT: The image often shows a task with multiple distinct parts (e.g., Part A, Part B, Part C). You MUST analyze and provide answers for ALL these parts comprehensively.
- 'identified_question': This field is crucial. It should be a single string that concatenates the core question text or instructions from ALL visible parts of the task.
    - Example for Part A (fill-in-the-blanks as seen in the image): "Part A: Use the spreadsheet's Average function... The mean value of people who would purchase the red box is {{part_A_mean_red_box}}. The mean value of people who would purchase the blue box is {{part_A_mean_blue_box}}."
    - Example for Part B (multiple choice): "Part B: What is the difference of the sample means of those who would purchase the red box and those who would purchase the blue box?"
    - Example for Part C (dropdowns/table completion): "Part C: Use the standard deviation values... The sample size of the session regarding the number of people who would purchase the red box, N1, is {{part_C_N1_dropdown_placeholder}}. The sample size of the session regarding the number of people who would purchase the blue box, N2, is {{part_C_N2_dropdown_placeholder}}. The standard deviation of the sample mean differences is approximately {{part_C_std_dev_diff_dropdown_placeholder}}."
    - Combine these into the 'identified_question' like: "Part A: Use the spreadsheet's Average function... The mean value of people who would purchase the red box is {{part_A_mean_red_box}}. The mean value of people who would purchase the blue box is {{part_A_mean_blue_box}}. Part B: What is the difference of the sample means of those who would purchase the red box and those who would purchase the blue box? Part C: Use the standard deviation values... The sample size of the session regarding the number of people who would purchase the red box, N1, is {{part_C_N1_dropdown_placeholder}}. The sample size of the session regarding the number of people who would purchase the blue box, N2, is {{part_C_N2_dropdown_placeholder}}. The standard deviation of the sample mean differences is approximately {{part_C_std_dev_diff_dropdown_placeholder}}."
- 'answers' array: You will create answer objects for EACH question item within EACH part.
    - For fill-in-the-blank answers (like in Part A), create 'direct_answer' items. The 'answer_id' MUST match the placeholder used in your 'identified_question' (e.g., "part_A_mean_red_box", "part_A_mean_blue_box").
    - For multiple-choice answers (like in Part B), list all options as 'multiple_choice_option' items. Their 'answer_id' should be descriptive and include the part, (e.g., "part_B_mc_option_1.74", "part_B_mc_option_1.86"). Indicate the correct one with 'is_correct_option': true.
    - For dropdown answers (like in Part C), create 'dropdown_choice' items. The 'answer_id' could match a placeholder from 'identified_question' (e.g., "part_C_N1_dropdown_placeholder") or be descriptive like "part_C_dropdown_N1_selection". The 'dropdown_selection_data.dropdown_id' MUST match the ID from the appended textual dropdown options (e.g., "dd_ctx_1").
- CRITICAL REMINDER: Ensure every distinct question item from ALL parts (A, B, C, etc.) is addressed in your response. Do not omit any part. Even if specific data (like dropdown options) is provided for only one part, you must still process all other visible parts of the question from the image. Prioritize complete coverage of the entire task.

**Special Equation Handling:**
If the question involves completing a visual mathematical equation with specific slots for mean, standard deviation, and sample size (typically appearing as `[value1] ± [value2] / √([value3])`), format the `identified_question` field like this:
`EQUATION_FORMULA:: {{mean_placeholder}} ± {{std_dev_placeholder}} / √({{n_placeholder}})`
Replace `mean_placeholder`, `std_dev_placeholder`, and `n_placeholder` with unique, descriptive names (e.g., `mean_electric_bill`, `std_dev_electric_bill`, `sample_size_electric_bill`).
Then, provide `direct_answer` items in the `answers` array for each of these placeholders, using the placeholder name as the `answer_id`. For example:
`{"answer_id": "mean_electric_bill", "text_content": "98.75", "content_type": "direct_answer", ...}`
`{"answer_id": "std_dev_electric_bill", "text_content": "10.45", "content_type": "direct_answer", ...}`
`{"answer_id": "sample_size_electric_bill", "text_content": "60", "content_type": "direct_answer", ...}`
If there is any text preceding or following the equation in the image, include it in the `identified_question` field before or after the `EQUATION_FORMULA::` template respectively. For example: "Complete the equation: EQUATION_FORMULA:: {{mean}} ± {{numerator}} / √({{denominator_n}}) This represents the confidence interval."

If the question is a **matching pairs** or **drag-to-image** type (e.g., "Match each sound device to the correct excerpt" or "Drag each tile to the correct location on the image"):
- 'identified_question' should describe the matching task. (Ensure this is compatible with the multi-part 'identified_question' structure if applicable).
- For each pair, create an object in 'answers' with 'content_type': 'matching_pair':
  - 'pair_data':
    - For text-to-text matching: {'term': 'Item from left column', 'match': 'Matched item from right column/list'}
    - For drag-to-image questions: {'term': 'Brief description of visual element (e.g., "pie chart", "China map")', 'match': 'Full text of the draggable description to be matched to this visual'}
  - 'is_correct_option': true
  - 'confidence': Your confidence score (0.0-1.0)
  - 'explanation': Optional explanation for why this match is correct
  - 'answer_id': Use sequential IDs like 'match_pair_1', 'match_pair_2', etc. (Or 'part_X_match_pair_1' if part of a larger multi-part question)

**CRITICAL for Drag-to-Image Questions**: When you see a grid of visual elements (images, charts, maps, diagrams) with draggable text boxes below:
- Identify each visual element in the grid (left-to-right, top-to-bottom)
- Match each visual to its corresponding text description
- In 'pair_data':
  - 'term' = short description of the visual (e.g., "Your Money (pie chart)", "China map", "Empire State Building")
  - 'match' = the exact draggable text that should be placed on this visual
- Create one matching_pair object for EACH visual element

If the question requires **arranging items in a sequence** (e.g., "Arrange the graphs in order"):
- 'identified_question' should describe the sequencing task. (Ensure this is compatible with the multi-part 'identified_question' structure if applicable).
- Create one object in 'answers' with 'content_type': 'ordered_sequence', 'answer_id': 'sequence_1'. (Ensure 'answer_id' incorporates part information like 'part_X_sequence_1' if part of a larger multi-part question).
- This item must have 'sequence_data': {'items': ["Item1_in_correct_order", "Item2_in_correct_order", ...], 'prompt_text': 'Optional: The instruction for ordering'}.
- Also include 'is_correct_option': true, 'confidence', and an 'explanation' for the sequence.

If it's a **multiple-choice question** (options usually labeled A, B, C, D or with radio buttons/checkboxes):

**CRITICAL MULTIPLE CHOICE RULES - READ CAREFULLY:**

1. **IDENTIFY ALL OPTIONS**: List EVERY option visible in the image (A, B, C, D, etc.). Create a separate answer object for EACH option.

2. **EXACTLY ONE CORRECT ANSWER**:
   - Standard multiple choice = Mark ONLY ONE option with 'is_correct_option': true
   - All other options MUST have 'is_correct_option': false
   - NEVER mark multiple options as correct unless the question explicitly says "Select ALL that apply"
   - If unsure which is correct, mark your BEST GUESS as true, others as false

3. **UNIQUE LABELS**: Each option MUST have a unique label:
   - Use 'label': "A", "B", "C", "D" (or whatever labels appear in the image)
   - 'answer_id': Use format "mc_option_A", "mc_option_B", etc.
   - Prefix with part if multi-part: "part_B_mc_option_A"

4. **TEXT CONTENT**:
   - 'text_content' MUST contain ONLY the literal, verbatim text of that specific option
   - DO NOT add explanations, reasoning, or extra info to text_content
   - Each option must have DIFFERENT text_content (no duplicates!)

5. **CONFIDENCE SCORING**:
   - Correct answer: 'confidence': 0.90-1.0 (high confidence)
   - Incorrect answers: 'confidence': 0.1-0.6 (lower confidence)
   - Use confidence to indicate how certain you are, NOT to mark correctness
   - is_correct_option is the ONLY indicator of correctness

6. **STRUCTURE**:
   - 'identified_question': The question stem/prompt
   - 'answers' array: One object per option with structure:
     ```json
     {
       "answer_id": "mc_option_A",
       "label": "A",
       "content_type": "multiple_choice_option",
       "text_content": "Exact text of option A from image",
       "is_correct_option": true,  // ONLY for the ONE correct answer
       "confidence": 0.95,  // High for correct, low for incorrect
       "explanation": "Why this is correct (optional)"
     }
     ```

**EXAMPLE - Correct Multiple Choice Response:**
```json
{
  "answers": [
    {"answer_id": "mc_option_A", "label": "A", "content_type": "multiple_choice_option",
     "text_content": "The theme is love", "is_correct_option": true, "confidence": 0.95},
    {"answer_id": "mc_option_B", "label": "B", "content_type": "multiple_choice_option",
     "text_content": "The theme is war", "is_correct_option": false, "confidence": 0.3},
    {"answer_id": "mc_option_C", "label": "C", "content_type": "multiple_choice_option",
     "text_content": "The theme is nature", "is_correct_option": false, "confidence": 0.2},
    {"answer_id": "mc_option_D", "label": "D", "content_type": "multiple_choice_option",
     "text_content": "The theme is death", "is_correct_option": false, "confidence": 0.4}
  ]
}
```

Notice: Only option A is marked correct, all have unique text, confidence varies, labels are A/B/C/D.

If it's a **text selection / hot text question** (select excerpts from a passage):

**CRITICAL TEXT SELECTION RULES:**

1. **INCLUDE FULL PASSAGE**: The 'identified_question' field MUST contain the COMPLETE passage text that excerpts are selected from
   - Example: "Select the correct text in the passage.\n\n[FULL PASSAGE TEXT HERE]"
   - Do NOT just describe the passage - include ALL the text

2. **ANSWER FORMAT**: Each selected excerpt should be a separate answer object:
   ```json
   {
     "answer_id": "text_selection_1",
     "content_type": "text_selection",
     "text_content": "The exact excerpt text from the passage",
     "is_correct_option": true,
     "confidence": 0.95,
     "explanation": "Why this excerpt answers the question"
   }
   ```

3. **STRUCTURE EXAMPLE**:
   ```json
   {
     "initial_analysis": {
       "question_type": "text_selection",
       "edmentum_type_name": "Hot Text (Text Selection)",
       "rendering_strategy": "edmentum_hot_text"
     },
     "identified_question": "Which excerpt from act I of Shakespeare's Twelfth Night informs the audience that Olivia has gone into a self-imposed seclusion?\n\nDUKE: Why, so I do, the noblest that I have:\nO, when mine eyes did see Olivia first,\nMethought she purg'd the air of pestilence!\n...[COMPLETE PASSAGE TEXT]...",
     "answers": [
       {
         "answer_id": "text_selection_1",
         "content_type": "text_selection",
         "text_content": "CAPTAIN: A virtuous maid, the daughter of a count\nThat died some twelvemonth since, then leaving her\nIn the protection of his son, her brother,\nWho shortly also died, for whose dear love,\nThey say, she hath abjured the company\nAnd sight of men.",
         "is_correct_option": true,
         "confidence": 0.95
       }
     ]
   }
   ```

4. **WHY THIS MATTERS**: The UI will display the full passage with selected excerpts highlighted in blue, matching Edmentum's hot text display.

**Regarding Dropdown Menus and Provided Options:**
When you encounter a question item in the image:
1.  First, **visually assess the item in the image**. Does it clearly look like a dropdown menu (e.g., a box with a selection arrow, a list that implies selection, or an explicit instruction to select from options that are *visually part of that question element*)?
2.  **If, and only if, you visually identify an element as a dropdown menu for a specific question or sub-part of a question**:
    a.  THEN, check if textual dropdown options (usually with IDs like `dd_ctx_1`, `dd_ctx_2`, etc.) have been provided at the end of this prompt.
    b.  If such textual options ARE provided, **critically assess which `dd_ctx_` ID and its associated options are relevant for THIS SPECIFIC VISUAL DROPDOWN you are currently analyzing.** Do not arbitrarily assign `dd_ctx_` data to non-dropdown elements or to visual dropdowns for which the provided textual options seem clearly mismatched (e.g., text options like 'High'/'Low' for a visual dropdown that clearly expects a specific year).
    c.  If you find a visual dropdown in the image AND relevant textual options for it are provided:
        i.  You should use `content_type: 'dropdown_choice'`.
        ii. 'answer_id': Ensure this is specific to the part and the dropdown (e.g., "part_C_N1_selection", or matching a placeholder like `{{part_C_N1_dropdown_placeholder}}` from `identified_question`).
        iii. 'dropdown_selection_data':
            -   `dropdown_id`: This MUST be the ID from the textually provided options (e.g., `dd_ctx_1`) that you've matched to this visual dropdown.
            -   `selected_text`: The text of the option you chose from the provided textual list for this specific dropdown.
            -   `selected_value`: The value of the option if available from the textual list, else null.
        iv. Include `is_correct_option`: true, `confidence`, and `explanation`.
3.  **If an element visually appears to be a dropdown, but no relevant textual options are provided for it, or the provided options are clearly unsuitable for that specific visual dropdown**:
    a.  Do NOT use `content_type: 'dropdown_choice'`.
    b.  Treat it as a fill-in-the-blank if it's a blank to be filled. You can note in your `explanation` for that item that it appeared to be a dropdown but usable/relevant options were not available in the textual data provided, or that the provided options were mismatched.
4.  **Crucially, do NOT assume that just because `dd_ctx_` variables are present in the textual prompt, they must be used or that they apply to any arbitrary question part.** For instance, if Part A of the question in the image shows a simple blank line for a short text answer (a typical fill-in-the-blank), you MUST NOT attempt to answer it using `content_type: 'dropdown_choice'` or force `dd_ctx_` data onto it. Your primary guide for identifying a question element as a dropdown and applying `dd_ctx_` data is the **visual evidence in the image for that specific item**, followed by a careful matching to any relevant textual options provided. Radio buttons or checkboxes are NOT to be treated as dropdowns under this logic; use multiple-choice instructions for them.

If it is an **open-ended question OR a fill-in-the-blank question** (that is NOT the special equation format or a dropdown handled above):
- **'identified_question'**: The FULL original sentence or question context, explicitly using unique placeholders like `{{part_A_blank_1}}`, `{{part_A_blank_2}}`, etc., for EACH blank, will be part of the concatenated 'identified_question' as per the main multi-part instruction. If the question implies a calculation you cannot perform (e.g., 'use spreadsheet'), but the answer value is explicitly stated or shown in a table within the image, use that visible value for the 'text_content'.
- For **each individual blank** identified by a placeholder in 'identified_question', create a **separate item** in the 'answers' array.
- Each such item must have:
    - 'content_type': 'direct_answer'.
    - 'answer_id': This MUST EXACTLY MATCH the placeholder used in 'identified_question' (e.g., "part_A_blank_1", "part_A_blank_2").
    - 'text_content': Your answer for that specific blank.
    - 'is_correct_option': true (as it's a direct answer you are providing).
    - 'confidence': Your confidence in this answer for the blank.
    - 'explanation': Optional explanation for this specific blank's answer.

If the question involves **completing a table**:
- 'identified_question' should describe the table completion task (this will be part of the concatenated 'identified_question' as per the main multi-part instruction).
- The 'answers' array should contain one item with 'content_type': 'table_completion', 'answer_id':'part_X_table_1' (where X is the part identifier if applicable).
- This item must have 'table_data' containing:
    - 'headers': A list of strings for column headers.
    - 'rows': A list of row objects. Each row object must have a 'row_cells' field, which is a list of cell objects.
    - Each cell object in 'row_cells' must have: 'header_name': (string) The header for that cell, 'value': (string) The data for that cell, 'is_ai_provided': (boolean) True if you are filling this cell, false if it was pre-filled in the image.
- Also include 'is_correct_option': true, 'confidence', and an 'explanation'.

Extract text accurately. If dropdown options are provided textually, use them specifically according to the refined dropdown instructions above.
The goal is to answer the question from the image as accurately as possible according to the described JSON schema and question type logic. Ensure all parts of a multi-part question are addressed.
If, for any question type, after following all guidelines, you determine that the provided data (like specific dropdown options for a visual dropdown) is fundamentally inconsistent or inappropriate for the question visible in the image (e.g., clearly textual options for a question demanding a purely numerical answer from a dropdown), you should reflect this in your 'explanation' for that answer item and indicate why a confident answer based on the provided options isn't possible.
If any part of the question or an answer involves a numeric value that you cannot determine (and it's not a case of mismatched dropdown options), represent it as the literal string "UNKNOWN_NUMERIC_VALUE" within the 'text_content' or relevant field, rather than 'None' or '【None】'.
"""
        final_prompt = base_prompt
        if hasattr(self, 'current_dropdown_data') and self.current_dropdown_data:
            dropdown_info_text = "\n\nThe following dropdown options were identified on the page (use their IDs like 'dd_ctx_1', 'dd_ctx_2' when referring to them in your 'dropdown_selection_data'):\n"
            for dropdown in self.current_dropdown_data:
                options_str_list = [f"'{opt.get('text','N/A')}' (value: '{opt.get('value','N/A')}')" for opt in dropdown.get('options', [])]; options_str = ", ".join(options_str_list)
                dropdown_info_text += f"- ID '{dropdown.get('id', 'Unknown Dropdown')}': [{options_str}]\n"
            final_prompt += dropdown_info_text; print(f"📋 Appending {len(self.current_dropdown_data)} dropdown(s) to prompt")
        threading.Thread(target=self._call_ai_api_thread_target, args=(api_key, selected_model, self.current_image_path, final_prompt),daemon=True).start()

    def _call_ai_api_thread_target(self, api_key, model_name, image_path, prompt):
        start_time = time.time()
        print(f"🤖 Starting AI analysis...")
        
        # Pre-encode image with cache validation
        # CRITICAL: Validate cache is for the CORRECT image to prevent answer contamination
        if self.current_image_base64 and self.current_image_base64_path == image_path:
            print(f"✅ Using cached base64 for '{os.path.basename(image_path)}' (instant!)")
        else:
            if self.current_image_base64_path and self.current_image_base64_path != image_path:
                print(f"⚠️ Cache invalidated: was for '{os.path.basename(self.current_image_base64_path)}', need '{os.path.basename(image_path)}'")
            encode_start = time.time()
            print(f"🔄 Encoding image: {os.path.basename(image_path)}")
            with open(image_path, "rb") as f:
                self.current_image_base64 = base64.b64encode(f.read()).decode('utf-8')
            self.current_image_base64_path = image_path  # Track which image this cache is for

        self.streaming_active = True
        self.accumulated_response = ""
        first_render_time = None
        last_ui_update_time = [0]  # Use list for mutable reference
        pending_data = [None]  # Store pending render data

        # PHASE 2: Progressive rendering callback with debouncing
        def stream_chunk_callback(chunk_text, full_accumulated):
            nonlocal first_render_time

            self.accumulated_response = full_accumulated
            char_count = len(full_accumulated)

            # Debounce UI updates - only update every 150ms to reduce overhead
            current_time = time.time()
            time_since_last_update = current_time - last_ui_update_time[0]

            # Update button text (less frequently)
            if time_since_last_update >= 0.2:  # 200ms debounce for button text
                self.after(0, lambda: self.ai_button.configure(text=f"⚡ Streaming... ({char_count} chars)"))

            # Progressive parsing and rendering
            if PROGRESSIVE_PARSER_AVAILABLE and hasattr(self, 'progressive_parser'):
                # Check if parser still exists (not cleared by user clicking capture during streaming)
                if self.progressive_parser is not None:
                    has_new, new_data = self.progressive_parser.add_chunk(chunk_text)
                    if has_new:
                        # Batch render updates - only render if enough time has passed
                        if time_since_last_update >= 0.15:  # 150ms debounce for renders
                            # Capture data to avoid lambda closure issue
                            data_to_render = new_data.copy() if isinstance(new_data, dict) else new_data
                            self.after(0, lambda data=data_to_render: self._render_progressive_content(data))
                            last_ui_update_time[0] = current_time
                        else:
                            # Store for next batch
                            pending_data[0] = new_data

            # Log first render time
            if first_render_time is None:
                first_render_time = time.time()
                print(f"⚡ TIME-TO-FIRST-RENDER: {(first_render_time - start_time) * 1000:.0f}ms")
        
        # Call streaming API with callback
        raw_ai_response_data = get_openrouter_response_streaming(
            api_key,
            model_name,
            self.current_image_base64,
            prompt,
            chunk_callback=stream_chunk_callback
        )

        # Flush any pending render data
        if pending_data[0] is not None:
            data_to_render = pending_data[0].copy() if isinstance(pending_data[0], dict) else pending_data[0]
            self.after(0, lambda data=data_to_render: self._render_progressive_content(data))
            pending_data[0] = None

        self.streaming_active = False
        total_time = (time.time() - start_time) * 1000
        print(f"⏱️ TOTAL STREAM TIME: {total_time:.0f}ms")
        
        # Update usage stats
        usage_data = raw_ai_response_data.get('_usage_data', {})
        if usage_data:
            self.after(0, lambda: self.update_session_usage(usage_data))
        
        # PHASE 3: Finalize display
        self.after(0, lambda: self._finalize_stream_display(raw_ai_response_data))

    def _create_skeleton_for_type(self, answer_type: str, answer_id: str = "", label: str = "") -> ctk.CTkFrame:
        """
        Create a skeleton loading placeholder for a specific answer type

        Args:
            answer_type: The content_type (e.g., "multiple_choice_option", "matching_pair")
            answer_id: Unique identifier for this answer
            label: Optional display label (e.g., "A", "B", "#1")

        Returns:
            CTkFrame containing the skeleton placeholder with loading animation
        """
        # Base skeleton frame with subtle animation-ready styling
        skeleton_frame = ctk.CTkFrame(
            self.progressive_answers_container,
            fg_color=("gray90", "gray20"),
            corner_radius=8,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        skeleton_frame.pack(fill="x", padx=5, pady=4)

        if answer_type == "multiple_choice_option":
            # Multiple choice skeleton: [Letter Badge] Loading text...
            inner_frame = ctk.CTkFrame(skeleton_frame, fg_color="transparent")
            inner_frame.pack(fill="x", padx=10, pady=8)

            # Letter badge placeholder
            badge_label = ctk.CTkLabel(
                inner_frame,
                text=label if label else "○",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("gray80", "gray35"),
                corner_radius=12,
                width=28,
                height=28,
                text_color=("gray50", "gray60")
            )
            badge_label.pack(side="left", padx=(0, 8))

            # Loading text placeholder
            text_label = ctk.CTkLabel(
                inner_frame,
                text="● ● ●  Loading answer...",
                font=ctk.CTkFont(size=13),
                text_color=("gray60", "gray50"),
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True)

        elif answer_type == "matching_pair":
            # Matching pair skeleton: Term ➡️ Loading match...
            inner_frame = ctk.CTkFrame(skeleton_frame, fg_color="transparent")
            inner_frame.pack(fill="x", padx=10, pady=8)

            # Pair number badge
            pair_badge = ctk.CTkLabel(
                inner_frame,
                text=label if label else "◆",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=("gray80", "gray35"),
                corner_radius=10,
                width=24,
                height=24,
                text_color=("gray50", "gray60")
            )
            pair_badge.pack(side="left", padx=(0, 8))

            # Loading content
            content_label = ctk.CTkLabel(
                inner_frame,
                text="Loading term ➡️ Loading match...",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray50"),
                anchor="w"
            )
            content_label.pack(side="left", fill="x", expand=True)

        elif answer_type == "text_selection":
            # Text selection skeleton: [#N] Loading selected text...
            inner_frame = ctk.CTkFrame(skeleton_frame, fg_color="transparent")
            inner_frame.pack(fill="x", padx=10, pady=8)

            # Number badge
            num_badge = ctk.CTkLabel(
                inner_frame,
                text=label if label else "#?",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=("gray80", "gray35"),
                corner_radius=10,
                width=32,
                height=24,
                text_color=("gray50", "gray60")
            )
            num_badge.pack(side="left", padx=(0, 8))

            # Loading text
            text_label = ctk.CTkLabel(
                inner_frame,
                text="● ● ●  Loading selected text...",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray50"),
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True)

        elif answer_type == "dropdown_choice":
            # Dropdown skeleton: [▼] Loading selection...
            inner_frame = ctk.CTkFrame(skeleton_frame, fg_color="transparent")
            inner_frame.pack(fill="x", padx=10, pady=8)

            # Dropdown icon
            dropdown_icon = ctk.CTkLabel(
                inner_frame,
                text="▼",
                font=ctk.CTkFont(size=12),
                fg_color=("gray80", "gray35"),
                corner_radius=6,
                width=24,
                height=24,
                text_color=("gray50", "gray60")
            )
            dropdown_icon.pack(side="left", padx=(0, 8))

            # Loading text
            text_label = ctk.CTkLabel(
                inner_frame,
                text=f"{label}: " if label else "" + "● ● ●  Loading selection...",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray50"),
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True)

        elif answer_type == "direct_answer":
            # Direct answer skeleton: Simple loading text
            inner_frame = ctk.CTkFrame(skeleton_frame, fg_color="transparent")
            inner_frame.pack(fill="x", padx=10, pady=8)

            text_label = ctk.CTkLabel(
                inner_frame,
                text=f"{label}: " if label else "" + "● ● ●  Loading answer...",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray50"),
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True)

        else:
            # Generic skeleton for unknown types
            inner_frame = ctk.CTkFrame(skeleton_frame, fg_color="transparent")
            inner_frame.pack(fill="x", padx=10, pady=8)

            text_label = ctk.CTkLabel(
                inner_frame,
                text="● ● ●  Loading...",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray50"),
                anchor="w"
            )
            text_label.pack(padx=5, pady=3)

        return skeleton_frame

    def _create_edmentum_mc_skeleton(self, letter: str, answer_id: str) -> ctk.CTkFrame:
        """Create multiple choice skeleton in Edmentum format"""
        is_dark = ctk.get_appearance_mode() == "Dark"

        skeleton = ctk.CTkFrame(
            self.progressive_answers_container,
            fg_color=(get_edmentum_color('gray_light', False), get_edmentum_color('gray_light', True)),
            corner_radius=EDMENTUM_SKELETON_STYLES['border_radius'],
            border_width=1,
            border_color=(get_edmentum_color('gray_border', False), get_edmentum_color('gray_border', True)),
            height=50
        )
        skeleton.pack(fill="x", pady=EDMENTUM_SKELETON_STYLES['margin_option'])

        inner = ctk.CTkFrame(skeleton, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        # Badge (letter)
        badge = ctk.CTkFrame(inner, width=32, height=32, corner_radius=16,
                            fg_color=(get_edmentum_color('gray_border', False), get_edmentum_color('gray_border', True)))
        badge.pack(side="left", padx=(0, 12))
        badge.pack_propagate(False)

        badge_label = ctk.CTkLabel(badge, text=letter, font=("Arial", 14, "bold"),
                                   text_color=(get_edmentum_color('gray_text', False), get_edmentum_color('gray_text', True)))
        badge_label.place(relx=0.5, rely=0.5, anchor="center")

        # Loading text
        loading_label = ctk.CTkLabel(inner, text="Loading answer...",
                                     font=(EDMENTUM_SKELETON_STYLES['font_family'], EDMENTUM_SKELETON_STYLES['font_size_option']),
                                     text_color=(get_edmentum_color('gray_text', False), get_edmentum_color('gray_text', True)))
        loading_label.pack(side="left", fill="x", expand=True)

        return skeleton

    def _create_edmentum_matching_skeleton(self, pair_num: int, answer_id: str) -> ctk.CTkFrame:
        """Create matching pair skeleton in Edmentum format"""
        skeleton = ctk.CTkFrame(
            self.progressive_answers_container,
            fg_color="transparent",
            height=50
        )
        skeleton.pack(fill="x", pady=4)

        # Number badge
        badge = ctk.CTkLabel(skeleton, text=str(pair_num), font=("Arial", 13, "bold"),
                            fg_color=(get_edmentum_color('gray_light', False), get_edmentum_color('gray_light', True)),
                            corner_radius=14, width=28, height=28,
                            text_color=(get_edmentum_color('gray_text', False), get_edmentum_color('gray_text', True)))
        badge.pack(side="left", padx=(0, 12))

        # Loading text
        loading_label = ctk.CTkLabel(skeleton, text="Loading term ➡️ Loading match...",
                                     font=("Arial", 13),
                                     text_color=(get_edmentum_color('gray_text', False), get_edmentum_color('gray_text', True)))
        loading_label.pack(side="left", fill="x", expand=True)

        return skeleton

    def _create_edmentum_hottext_skeleton(self, selection_num: int, answer_id: str) -> ctk.CTkFrame:
        """Create hot text selection skeleton in Edmentum format"""
        skeleton = ctk.CTkFrame(
            self.progressive_answers_container,
            fg_color=(get_edmentum_color('green_light', False), get_edmentum_color('green_light', True)),
            corner_radius=8,
            border_width=2,
            border_color=(get_edmentum_color('green_correct', False), get_edmentum_color('green_correct', True)),
            height=50
        )
        skeleton.pack(fill="x", pady=5, padx=15)

        # Loading text for selection
        loading_label = ctk.CTkLabel(skeleton, text="Loading selection...",
                                     font=("Arial", 18, "bold"),
                                     text_color=(get_edmentum_color('green_correct', False), get_edmentum_color('green_correct', True)))
        loading_label.pack(fill="both", expand=True, padx=15, pady=10)

        return skeleton

    def _create_skeletons_from_metadata(self, metadata: Dict):
        """
        Create skeleton placeholders in FINAL Edmentum format based on rendering strategy
        This eliminates the two-stage rendering latency

        Args:
            metadata: The metadata object with question_type, total_answers, and answer_structure
        """
        if not metadata or not isinstance(metadata, dict):
            print("⚠️ Invalid metadata, skipping skeleton creation")
            return

        # Get rendering strategy from cached analysis
        strategy = ''
        if hasattr(self, 'cached_analysis') and isinstance(self.cached_analysis, dict):
            strategy = self.cached_analysis.get('rendering_strategy', '')

        answer_structure = metadata.get("answer_structure", [])
        if not answer_structure:
            return

        print(f"🎨 Creating {len(answer_structure)} skeleton placeholders...")

        # Create skeletons based on rendering strategy
        if strategy == 'edmentum_multiple_choice':
            # Multiple choice: Create Edmentum-styled MC skeletons
            for i, answer_spec in enumerate(answer_structure):
                answer_id = answer_spec.get("id", f"mc_option_{chr(65+i)}")
                letter = chr(65 + i)  # A, B, C, D
                skeleton = self._create_edmentum_mc_skeleton(letter, answer_id)
                self.skeleton_frames[answer_id] = skeleton

        elif strategy == 'edmentum_matching':
            # Matching pairs: Create Edmentum-styled matching skeletons
            for i, answer_spec in enumerate(answer_structure):
                answer_id = answer_spec.get("id", f"matching_pair_{i+1}")
                skeleton = self._create_edmentum_matching_skeleton(i + 1, answer_id)
                self.skeleton_frames[answer_id] = skeleton

        elif strategy == 'edmentum_hot_text':
            # Hot text: Create Edmentum-styled selection skeletons
            for i, answer_spec in enumerate(answer_structure):
                answer_id = answer_spec.get("id", f"hot_text_{i+1}")
                skeleton = self._create_edmentum_hottext_skeleton(i + 1, answer_id)
                self.skeleton_frames[answer_id] = skeleton

        else:
            # Fallback: Use generic skeletons for unknown strategies
            for answer_spec in answer_structure:
                answer_type = answer_spec.get("type", "generic")
                answer_id = answer_spec.get("id", f"skeleton_{len(self.skeleton_frames)}")
                label = answer_spec.get("label", "")
                skeleton = self._create_skeleton_for_type(answer_type, answer_id, label)
                self.skeleton_frames[answer_id] = skeleton

    def _render_progressive_content(self, new_data: Dict):
        """Render newly complete JSON objects as formatted UI elements (PHASE 2)"""
        try:
            if not isinstance(new_data, dict):
                print(f"⚠️ Progressive render received non-dict data: {type(new_data)}")
                return

            # PRIORITY 0: Handle initial_analysis first - cache but don't display
            if "initial_analysis" in new_data and not hasattr(self, 'analysis_displayed'):
                analysis = new_data["initial_analysis"]
                self.cached_analysis = analysis  # Store for skeleton rendering
                self.analysis_displayed = True
                print(f"🔍 Analysis parsed (not displayed)")

            # PRIORITY 1: Handle metadata - create skeleton placeholders
            if "metadata" in new_data:
                metadata = new_data["metadata"]
                print(f"🎨 Metadata received, creating skeleton placeholders")
                self._create_skeletons_from_metadata(metadata)

            # Update status if question identified
            if "identified_question" in new_data:
                question = new_data["identified_question"]
                if hasattr(self, 'streaming_status_label') and self.streaming_status_label.winfo_exists():
                    self.streaming_status_label.configure(text=f"📝 {question[:80]}...")

            # Render new answers progressively as formatted elements
            # If skeleton exists for this answer_id, replace it; otherwise create new element
            if "new_answers" in new_data:
                for answer in new_data["new_answers"]:
                    try:
                        answer_id = answer.get("answer_id", "")

                        # Normalize ID format (match_pair_X == matching_pair_X)
                        # Some AI models use "match_pair" while skeletons use "matching_pair"
                        actual_skeleton_id = answer_id
                        if answer_id and answer_id not in self.skeleton_frames:
                            # Try common variations
                            variations = [
                                answer_id.replace("match_pair", "matching_pair"),
                                answer_id.replace("matching_pair", "match_pair"),
                                answer_id.replace("mc_option", "multiple_choice"),
                                answer_id.replace("multiple_choice", "mc_option")
                            ]
                            for variant in variations:
                                if variant in self.skeleton_frames:
                                    actual_skeleton_id = variant
                                    break

                        # Check if we have a skeleton for this answer
                        if actual_skeleton_id and actual_skeleton_id in self.skeleton_frames:
                            self._replace_skeleton_with_answer(actual_skeleton_id, answer)
                        else:
                            # No skeleton exists, render normally (fallback mode)
                            print(f"   ➕ No skeleton for {answer_id}, rendering directly")
                            self._add_progressive_answer_item(answer)
                    except Exception as item_error:
                        print(f"⚠️ Failed to render answer item: {item_error}")
                        print(f"   Item data: {answer}")

        except Exception as e:
            print(f"❌ Progressive render error: {e}")
            import traceback
            traceback.print_exc()

    def _replace_skeleton_with_answer(self, answer_id: str, answer_item: Dict):
        """
        Update skeleton placeholder with real answer data (TRUE progressive streaming)

        Instead of destroying and recreating, we update the skeleton's content in-place
        for smooth, flicker-free transitions.

        Args:
            answer_id: The ID of the answer/skeleton to replace
            answer_item: The complete answer data to render
        """
        if answer_id not in self.skeleton_frames:
            print(f"⚠️ Skeleton not found for {answer_id}")
            return

        skeleton_frame = self.skeleton_frames[answer_id]

        # Check if skeleton still exists (user might have cleared display)
        if not skeleton_frame.winfo_exists():
            print(f"⚠️ Skeleton widget no longer exists for {answer_id}")
            del self.skeleton_frames[answer_id]
            return

        # Update skeleton content in-place (no destroy/recreate)
        self._update_skeleton_content(skeleton_frame, answer_item)

        print(f"   ✓ Skeleton updated with real answer for {answer_id}")

        # Auto-scroll as answers stream in (debounced to avoid excessive scrolling)
        if not hasattr(self, '_scroll_pending') or not self._scroll_pending:
            self._scroll_pending = True
            self.after(300, self._debounced_scroll)

    def _update_skeleton_content(self, skeleton_frame: ctk.CTkFrame, answer_item: Dict):
        """
        Update skeleton frame content with actual answer data (in-place update)

        This creates smooth progressive streaming by updating existing widgets
        rather than destroying and recreating them.

        Args:
            skeleton_frame: The skeleton CTkFrame widget to update
            answer_item: The answer data to display
        """
        # Clear old skeleton content
        for widget in skeleton_frame.winfo_children():
            widget.destroy()

        content_type = answer_item.get("content_type", "text_plain")
        is_correct = answer_item.get("is_correct_option", False)
        confidence = answer_item.get("confidence")
        text_content = answer_item.get("text_content", "")

        # Update frame colors based on correctness
        if is_correct:
            skeleton_frame.configure(
                fg_color=("#e8f5e9", "#1a311a"),
                border_color=("#4CAF50", "#388E3C")
            )
        elif content_type == "matching_pair":
            skeleton_frame.configure(
                fg_color=("#e8f0fe", "#1c2333"),
                border_color=("#4a90e2", "#2a5298")
            )
        else:
            skeleton_frame.configure(
                fg_color=("gray80", "gray25"),
                border_color=("gray70", "gray30")
            )

        # Create content based on type
        inner_frame = ctk.CTkFrame(skeleton_frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=10, pady=8)

        # Type-specific rendering
        if content_type == "multiple_choice_option":
            self._render_mc_option_content(inner_frame, answer_item)
        elif content_type == "matching_pair":
            self._render_matching_pair_content(inner_frame, answer_item)
        elif content_type == "text_selection":
            self._render_text_selection_content(inner_frame, answer_item)
        else:
            # Generic text display
            text_label = ctk.CTkLabel(
                inner_frame,
                text=text_content if text_content else str(answer_item),
                font=ctk.CTkFont(size=12),
                wraplength=600,
                anchor="w"
            )
            text_label.pack(fill="x")

    def _render_mc_option_content(self, parent: ctk.CTkFrame, answer_item: Dict):
        """Render multiple choice option content"""
        label = answer_item.get('label', '?')
        text_content = answer_item.get('text_content', '')
        is_correct = answer_item.get('is_correct_option', False)

        # Letter badge
        badge_color = "#28A745" if is_correct else "#4a90e2"
        badge = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=badge_color,
            corner_radius=14,
            width=28,
            height=28,
            text_color="white"
        )
        badge.pack(side="left", padx=(0, 10))

        # Option text
        text_label = ctk.CTkLabel(
            parent,
            text=text_content,
            font=ctk.CTkFont(size=13),
            wraplength=520,
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True)

        # Checkmark if correct
        if is_correct:
            check = ctk.CTkLabel(
                parent,
                text="✓",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#28A745"
            )
            check.pack(side="right", padx=(10, 0))

    def _render_matching_pair_content(self, parent: ctk.CTkFrame, answer_item: Dict):
        """Render matching pair content"""
        pair_data = answer_item.get('pair_data', {})
        term = pair_data.get('term', '')
        match = pair_data.get('match', pair_data.get('match_value', ''))

        content_text = f"{term} ➡️ {match}"
        text_label = ctk.CTkLabel(
            parent,
            text=content_text,
            font=ctk.CTkFont(size=12),
            wraplength=600,
            anchor="w"
        )
        text_label.pack(fill="x")

    def _render_text_selection_content(self, parent: ctk.CTkFrame, answer_item: Dict):
        """Render text selection content"""
        text_content = answer_item.get('text_content', '')

        # For text selection, show excerpt with quote marks
        text_label = ctk.CTkLabel(
            parent,
            text=f'"{text_content}"',
            font=ctk.CTkFont(size=12),
            wraplength=600,
            anchor="w",
            justify="left"
        )
        text_label.pack(fill="x")

    def _add_progressive_answer_item(self, answer_item: Dict):
        """Add formatted answer item to progressive display with badge styling matching final display"""
        if not hasattr(self, 'progressive_answers_container') or not self.progressive_answers_container.winfo_exists():
            return

        content_type = answer_item.get("content_type", "text_plain")
        is_correct = answer_item.get("is_correct_option", False)
        confidence = answer_item.get("confidence")
        answer_id = answer_item.get("answer_id", "")
        text_content = answer_item.get("text_content", "")

        # Debug logging to diagnose streaming issues
        print(f"   🔍 Streaming answer: type={content_type}, id={answer_id}, is_correct={is_correct}, conf={confidence}")
        print(f"      Text: {text_content[:60]}..." if len(text_content) > 60 else f"      Text: {text_content}")

        # Filter out instructional text that shouldn't be displayed as answer cards
        if content_type == "multiple_choice_option" and text_content:
            text_lower = text_content.lower().strip()
            # Skip if it looks like instructions rather than actual answer content
            instructional_patterns = [
                "select the", "choose the", "click the", "drag the",
                "select a", "choose a", "click a", "drag a",
                "select all", "choose all", "identify the",
                "which of the following", "pick the"
            ]
            if any(pattern in text_lower for pattern in instructional_patterns):
                # Check if it's ONLY instructions (short and matches pattern exactly)
                if len(text_content.split()) < 10:  # Short text is more likely to be just instructions
                    print(f"      ⚠️ Skipping instructional text: {text_content}")
                    return

        # Determine frame colors based on correctness and content type
        if is_correct:
            base_fg_color = ("#e8f5e9", "#1a311a")
            base_border_color = ("#4CAF50", "#388E3C")
        elif content_type == "matching_pair":
            base_fg_color = ("#e8f0fe", "#1c2333")
            base_border_color = ("#4a90e2", "#2a5298")
        else:
            base_fg_color = ("gray80", "gray25")
            base_border_color = ("gray70", "gray30")

        # Create item frame
        item_frame = ctk.CTkFrame(
            self.progressive_answers_container,
            fg_color=base_fg_color,
            border_color=base_border_color,
            border_width=1,
            corner_radius=6
        )
        item_frame.pack(fill="x", padx=5, pady=3)

        # Render based on content type with badge styling
        if content_type == "multiple_choice_option":
            # Badge-style display for multiple choice (matching final display)
            badge_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            badge_frame.pack(fill="x", padx=10, pady=8)

            # Extract option letter (A, B, C, D)
            option_letter = self._extract_option_letter(answer_id)

            # Option letter badge (large, prominent)
            letter_fg_color = ("#4CAF50", "#2E7D32") if is_correct else ("#2196F3", "#1565C0")
            letter_badge = ctk.CTkLabel(
                badge_frame,
                text=option_letter,
                width=45,
                height=45,
                corner_radius=22,
                fg_color=letter_fg_color,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=("white", "white")
            )
            letter_badge.pack(side="left", padx=(0, 12))

            # Option text
            text_label = ctk.CTkLabel(
                badge_frame,
                text=text_content if text_content else "[Option Text]",
                wraplength=450,
                anchor="w",
                justify="left",
                font=ctk.CTkFont(size=13)
            )
            text_label.pack(side="left", fill="x", expand=True)

            # Confidence badge
            if confidence is not None:
                conf_percent = confidence * 100
                if confidence >= 0.9:
                    conf_color = ("#4CAF50", "#2E7D32")
                elif confidence >= 0.75:
                    conf_color = ("#FF9800", "#F57C00")
                else:
                    conf_color = ("#FF5722", "#D84315")

                conf_badge = ctk.CTkLabel(
                    badge_frame,
                    text=f"{conf_percent:.0f}%",
                    fg_color=conf_color,
                    corner_radius=12,
                    width=55,
                    height=28,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("white", "white")
                )
                conf_badge.pack(side="right", padx=(12, 0))
            else:
                # Show placeholder during streaming
                conf_badge = ctk.CTkLabel(
                    badge_frame,
                    text="...",
                    fg_color=("gray60", "gray40"),
                    corner_radius=12,
                    width=55,
                    height=28,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("white", "white")
                )
                conf_badge.pack(side="right", padx=(12, 0))

        elif content_type == "text_selection":
            # Badge-style display for text selection (matching final display)
            badge_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            badge_frame.pack(fill="x", padx=10, pady=8)

            # Extract image number from answer_id
            import re
            img_match = re.search(r'image[_-]?(\d+)', answer_id, re.IGNORECASE)
            img_num = img_match.group(1) if img_match else "?"

            # Image reference badge
            img_badge = ctk.CTkLabel(
                badge_frame,
                text=f"#{img_num}",
                width=45,
                height=45,
                corner_radius=22,
                fg_color=("#9C27B0", "#6A1B9A"),  # Purple for image reference
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("white", "white")
            )
            img_badge.pack(side="left", padx=(0, 12))

            # Selected text content
            text_label = ctk.CTkLabel(
                badge_frame,
                text=text_content if text_content else "[Selected Text]",
                wraplength=450,
                anchor="w",
                justify="left",
                font=ctk.CTkFont(size=13)
            )
            text_label.pack(side="left", fill="x", expand=True)

            # Confidence badge
            if confidence is not None:
                conf_percent = confidence * 100
                if confidence >= 0.9:
                    conf_color = ("#4CAF50", "#2E7D32")
                elif confidence >= 0.75:
                    conf_color = ("#FF9800", "#F57C00")
                else:
                    conf_color = ("#FF5722", "#D84315")

                conf_badge = ctk.CTkLabel(
                    badge_frame,
                    text=f"{conf_percent:.0f}%",
                    fg_color=conf_color,
                    corner_radius=12,
                    width=55,
                    height=28,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("white", "white")
                )
                conf_badge.pack(side="right", padx=(12, 0))
            else:
                # Show placeholder during streaming
                conf_badge = ctk.CTkLabel(
                    badge_frame,
                    text="...",
                    fg_color=("gray60", "gray40"),
                    corner_radius=12,
                    width=55,
                    height=28,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("white", "white")
                )
                conf_badge.pack(side="right", padx=(12, 0))

        elif content_type == "matching_pair":
            # Matching pair with improved styling
            pair_data = answer_item.get("pair_data", {})
            term = pair_data.get("term", "")
            match = pair_data.get("match", "")

            label = ctk.CTkLabel(
                item_frame,
                text=f"'{term}' ➡️ '{match}'",
                font=ctk.CTkFont(size=12),
                wraplength=600,
                anchor="w"
            )
            label.pack(padx=10, pady=6, fill="x")

        else:
            # Default display for other content types
            label = ctk.CTkLabel(
                item_frame,
                text=text_content if text_content else str(answer_item),
                font=ctk.CTkFont(size=12),
                wraplength=600,
                anchor="w"
            )
            label.pack(padx=10, pady=6, fill="x")

        print(f"   ✨ Rendered {content_type} progressively")
    
    def _append_streaming_chunk(self, chunk_text: str):
        """Append text chunk to streaming display in real-time (PHASE 2)"""
        if hasattr(self, 'streaming_textbox') and self.streaming_textbox.winfo_exists():
            try:
                self.streaming_textbox.configure(state="normal")
                self.streaming_textbox.insert("end", chunk_text)
                self.streaming_textbox.see("end")
                self.streaming_textbox.configure(state="disabled")
            except Exception as e:
                print(f"Chunk append error: {e}")
    
    def _show_validation_warnings(self, warnings: list):
        """
        Display validation warnings to the user

        Args:
            warnings: List of warning strings from validator
        """
        if not warnings or not hasattr(self, 'streaming_container'):
            return

        try:
            # Create a warning banner at the top
            warning_frame = ctk.CTkFrame(
                self.streaming_container,
                fg_color=("#FFF3CD", "#3D3416"),  # Warning yellow
                corner_radius=6,
                border_width=1,
                border_color=("#FFC107", "#8B6914")
            )
            warning_frame.pack(fill="x", padx=10, pady=(5, 10))

            # Header
            header_label = ctk.CTkLabel(
                warning_frame,
                text="⚠️ AI Response Issues Detected (Auto-Fixed)",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#856404", "#FFD700"),
                anchor="w"
            )
            header_label.pack(fill="x", padx=10, pady=(8, 4))

            # Warning messages
            for warning in warnings[:3]:  # Show first 3 warnings
                warning_label = ctk.CTkLabel(
                    warning_frame,
                    text=f"• {warning}",
                    font=ctk.CTkFont(size=11),
                    text_color=("#856404", "#FFD700"),
                    wraplength=650,
                    anchor="w",
                    justify="left"
                )
                warning_label.pack(fill="x", padx=20, pady=2)

            if len(warnings) > 3:
                more_label = ctk.CTkLabel(
                    warning_frame,
                    text=f"... and {len(warnings) - 3} more issues",
                    font=ctk.CTkFont(size=10),
                    text_color=("#856404", "#FFD700"),
                    anchor="w"
                )
                more_label.pack(fill="x", padx=20, pady=2)

            # Bottom padding
            ctk.CTkFrame(warning_frame, fg_color="transparent", height=6).pack()

        except Exception as e:
            print(f"Failed to display validation warnings: {e}")

    def _display_initial_analysis(self, analysis: Dict):
        """
        Display the initial AI analysis section at the top of the streaming container

        Args:
            analysis: initial_analysis dict from AI response
        """
        if not EDMENTUM_RENDERER_AVAILABLE:
            # Fallback: display simple text summary
            print("📊 Initial Analysis (Edmentum renderer not available, showing fallback)")
            if hasattr(self, 'streaming_container') and self.streaming_container.winfo_exists():
                analysis_text = f"Question Type: {analysis.get('edmentum_type_name', 'Unknown')}"
                analysis_label = ctk.CTkLabel(
                    self.streaming_container,
                    text=f"🔍 {analysis_text}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                )
                analysis_label.pack(fill="x", padx=10, pady=5)
            return

        try:
            # Use InitialAnalysisDisplay component to render analysis
            if hasattr(self, 'streaming_container') and self.streaming_container.winfo_exists():
                InitialAnalysisDisplay.create_analysis_display(self.streaming_container, analysis)
                print("✓ Initial analysis displayed")
        except Exception as e:
            print(f"⚠️ Failed to display initial analysis: {e}")
            import traceback
            traceback.print_exc()

    def _finalize_stream_display(self, raw_response_data):
        """PHASE 3: Process complete response and apply visual enhancements"""
        print("🎨 Finalizing display...")

        # Process response
        processed_data = self._process_ai_response_data(raw_response_data)

        # VALIDATION: Validate and auto-fix response before rendering
        if RESPONSE_VALIDATOR_AVAILABLE:
            print("🔍 Validating response...")
            processed_data, warnings = validate_response(processed_data)
            if warnings:
                # Display validation warnings to user
                self._show_validation_warnings(warnings)
        else:
            print("⚠️ Response validator not available, skipping validation")

        # Check if we should use Edmentum rendering
        should_use_edmentum = False
        analysis = processed_data.get('initial_analysis', {})
        rendering_strategy = analysis.get('rendering_strategy', 'standard_fallback')

        if EDMENTUM_RENDERER_AVAILABLE and rendering_strategy != 'standard_fallback':
            print(f"🎨 Attempting Edmentum rendering with strategy: {rendering_strategy}")
            should_use_edmentum = True

        # Clear streaming container only if NOT using Edmentum rendering
        # (Edmentum rendering needs to keep the initial_analysis display)
        if not should_use_edmentum:
            if hasattr(self, 'streaming_container') and self.streaming_container.winfo_exists():
                self.streaming_container.destroy()

        # Try Edmentum rendering if applicable
        if should_use_edmentum:
            success = self._render_edmentum_question(analysis, processed_data)
            if success:
                print("✓ Edmentum rendering successful")
                self.ai_button.configure(state="normal", text="Get AI Answer")
                # Auto-scroll to answers
                self.after(200, self._auto_scroll_to_answers)
                return
            else:
                print("⚠️ Edmentum rendering failed, falling back to standard display")
                # Clear streaming container for standard display
                if hasattr(self, 'streaming_container') and self.streaming_container.winfo_exists():
                    self.streaming_container.destroy()

        # Standard display (fallback)
        self.display_ai_answers(processed_data)
        self.ai_button.configure(state="normal", text="Get AI Answer")

        # Auto-scroll to answers
        self.after(200, self._auto_scroll_to_answers)

    def _render_edmentum_question(self, analysis: Dict, response_data: Dict) -> bool:
        """
        Render question using Edmentum visual style

        Args:
            analysis: initial_analysis dict
            response_data: Complete AI response data

        Returns:
            True if successful, False if should fall back to standard display
        """
        if not EDMENTUM_RENDERER_AVAILABLE:
            return False

        try:
            # DON'T destroy progressive answers - they have the green highlighting!
            # Just hide the streaming status label instead
            if hasattr(self, 'streaming_status_label') and self.streaming_status_label.winfo_exists():
                self.streaming_status_label.pack_forget()

            # Clear ONLY the initial analysis display from streaming container
            # Keep progressive_answers_container with its skeleton frames intact
            if hasattr(self, 'streaming_container') and self.streaming_container.winfo_exists():
                for widget in self.streaming_container.winfo_children():
                    # Keep the progressive_answers_container (has green highlights!)
                    if widget != self.progressive_answers_container:
                        widget.destroy()

            # Create renderer
            renderer = EdmentumQuestionRenderer()

            # Extract data
            question_text = response_data.get('identified_question', '')
            answers = response_data.get('answers', [])

            # Render into progressive_answers_container (which is inside streaming_container)
            if hasattr(self, 'progressive_answers_container') and self.progressive_answers_container.winfo_exists():
                success = renderer.render_question(
                    self.progressive_answers_container,
                    analysis,
                    question_text,
                    answers,
                    question_number=None
                )
                return success
            else:
                return False

        except Exception as e:
            print(f"❌ Edmentum rendering error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    # NOTE: It's recommended to run main.py instead of ui.py directly
    # main.py handles pre-launch updates more safely
    print("⚠️ You're running ui.py directly.")
    print("   For better update handling, run main.py instead.")
    print("   Launching app in 2 seconds...\n")
    time.sleep(2)

    try:
        app = HomeworkApp()
        app.mainloop()
    except Exception as e:
        print(f"\n[ERROR] Application failed to start!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
