"""
UI Export Module - Export CustomTkinter widget trees to structured JSON
Captures widget hierarchy, positions, text content, and styling
"""

import tkinter
from typing import Dict, List, Optional, Any


def export_widget_tree(widget, max_depth: int = 10, current_depth: int = 0) -> Optional[Dict]:
    """
    Recursively export widget tree to JSON-serializable dict

    Args:
        widget: Root widget to export (CTkFrame, CTkLabel, etc.)
        max_depth: Maximum recursion depth
        current_depth: Current recursion level (internal)

    Returns:
        Dict with widget structure and properties
    """
    if widget is None or current_depth >= max_depth:
        return None

    try:
        # Get widget type
        widget_type = widget.__class__.__name__

        # Get geometry (position and size)
        geometry = _get_widget_geometry(widget)

        # Get text content if applicable
        text_content = _get_widget_text(widget)

        # Get configuration
        config = _get_widget_config(widget)

        # Build widget data
        widget_data = {
            "type": widget_type,
            "geometry": geometry
        }

        if text_content:
            widget_data["text"] = text_content

        if config:
            widget_data["config"] = config

        # Get children recursively
        children = _get_widget_children(widget, max_depth, current_depth + 1)
        if children:
            widget_data["children"] = children

        return widget_data

    except Exception as e:
        # Return minimal data if export fails
        return {
            "type": "Unknown",
            "error": str(e)
        }


def _get_widget_geometry(widget) -> Dict[str, Any]:
    """Get widget position and size"""
    try:
        # Try to get actual rendered geometry
        if widget.winfo_exists():
            return {
                "x": widget.winfo_x(),
                "y": widget.winfo_y(),
                "width": widget.winfo_width(),
                "height": widget.winfo_height(),
                "visible": widget.winfo_viewable()
            }
    except:
        pass

    # Fallback to empty geometry
    return {"x": 0, "y": 0, "width": 0, "height": 0, "visible": False}


def _get_widget_text(widget) -> Optional[str]:
    """Extract text content from widget if available"""
    try:
        # CTkLabel, CTkButton - use cget('text')
        if hasattr(widget, 'cget'):
            try:
                text = widget.cget('text')
                if text and isinstance(text, str) and len(text) > 0:
                    # Truncate very long text
                    return text[:500] if len(text) > 500 else text
            except:
                pass

        # CTkTextbox, CTkEntry - use get()
        if hasattr(widget, 'get'):
            try:
                if hasattr(widget, 'get'):
                    # CTkTextbox uses get("1.0", "end")
                    text = widget.get("1.0", "end-1c") if hasattr(widget, 'insert') else widget.get()
                    if text and isinstance(text, str) and len(text.strip()) > 0:
                        return text[:500] if len(text) > 500 else text
            except:
                pass

    except Exception:
        pass

    return None


def _get_widget_config(widget) -> Dict[str, Any]:
    """Get widget configuration (colors, fonts, etc.)"""
    config = {}

    try:
        # Common properties to extract
        properties = ['fg_color', 'bg_color', 'text_color', 'border_color', 'border_width', 'corner_radius']

        for prop in properties:
            if hasattr(widget, 'cget'):
                try:
                    value = widget.cget(prop)
                    if value is not None:
                        config[prop] = str(value)
                except:
                    pass

    except Exception:
        pass

    return config if config else None


def _get_widget_children(widget, max_depth: int, current_depth: int) -> Optional[List[Dict]]:
    """Get all child widgets recursively"""
    children = []

    try:
        # Get widget children
        if hasattr(widget, 'winfo_children'):
            child_widgets = widget.winfo_children()

            for child in child_widgets:
                try:
                    child_data = export_widget_tree(child, max_depth, current_depth)
                    if child_data:
                        children.append(child_data)
                except:
                    continue

    except Exception:
        pass

    return children if children else None


def get_widget_summary(widget) -> Dict[str, Any]:
    """
    Get a lightweight summary of widget tree (for quick diagnostics)

    Returns counts of widget types and total depth
    """
    summary = {
        "total_widgets": 0,
        "max_depth": 0,
        "widget_counts": {}
    }

    def count_widgets(w, depth=0):
        if w is None:
            return

        summary["total_widgets"] += 1
        summary["max_depth"] = max(summary["max_depth"], depth)

        widget_type = w.__class__.__name__
        summary["widget_counts"][widget_type] = summary["widget_counts"].get(widget_type, 0) + 1

        try:
            if hasattr(w, 'winfo_children'):
                for child in w.winfo_children():
                    count_widgets(child, depth + 1)
        except:
            pass

    count_widgets(widget)
    return summary


# Test function for development
if __name__ == "__main__":
    import customtkinter as ctk

    print("=== UI Export Test ===\n")

    # Create test window
    root = ctk.CTk()
    root.title("Export Test")

    # Create test widgets
    frame = ctk.CTkFrame(root)
    frame.pack(padx=20, pady=20)

    label = ctk.CTkLabel(frame, text="Test Label")
    label.pack()

    button = ctk.CTkButton(frame, text="Test Button")
    button.pack()

    # Test export
    print("1. Exporting widget tree...")
    tree = export_widget_tree(frame)

    import json
    print(json.dumps(tree, indent=2))

    print("\n2. Getting summary...")
    summary = get_widget_summary(frame)
    print(json.dumps(summary, indent=2))

    print("\n=== Test Complete ===")
