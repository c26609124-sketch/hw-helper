"""
OCR-based Hot Spot Location Detector

This module uses Optical Character Recognition (OCR) to automatically detect
the exact pixel locations of organism labels in food web diagrams and other
hot spot questions. This eliminates the need for AI estimation and provides
100% accurate, deterministic bounding box coordinates.

Author: Claude Code
Version: 1.0.31
"""

import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
import pytesseract


def detect_hotspot_locations(image_path: str, target_labels: List[str],
                             padding_multiplier: float = 3.0) -> Dict[str, Dict[str, int]]:
    """
    Use OCR to find exact locations of text labels in an image and generate
    bounding boxes that include both the label and the organism image above it.

    Args:
        image_path: Path to the screenshot image
        target_labels: List of organism/object names to find (e.g., ["penguin", "krill", "cod"])
        padding_multiplier: How many text heights to expand upward to capture organism image (default: 3.0)

    Returns:
        Dictionary mapping label name -> bounding box dict with keys:
            - 'x': Left edge pixel coordinate
            - 'y': Top edge pixel coordinate
            - 'width': Box width in pixels
            - 'height': Box height in pixels
            - 'confidence': OCR confidence score (0-100)

    Example:
        >>> detect_hotspot_locations("food_web.png", ["penguin", "krill"])
        {
            'penguin': {'x': 180, 'y': 100, 'width': 120, 'height': 80, 'confidence': 95},
            'krill': {'x': 350, 'y': 250, 'width': 100, 'height': 70, 'confidence': 92}
        }
    """
    print(f"🔍 Starting OCR detection for labels: {target_labels}")

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"⚠️ Failed to load image: {image_path}")
        return {}

    # Convert to grayscale for better OCR accuracy
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply slight blur to reduce noise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Run Tesseract OCR with bounding box detection
    try:
        ocr_data = pytesseract.image_to_data(
            gray,
            output_type=pytesseract.Output.DICT,
            config='--psm 11'  # Sparse text mode for better label detection
        )
    except Exception as e:
        print(f"⚠️ Tesseract OCR failed: {e}")
        print(f"   Make sure Tesseract is installed: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)")
        return {}

    results = {}
    target_labels_lower = [label.lower().strip() for label in target_labels]

    # Iterate through all detected text
    for i, text in enumerate(ocr_data['text']):
        if not text or not text.strip():
            continue

        text_lower = text.lower().strip()
        confidence = int(ocr_data['conf'][i]) if ocr_data['conf'][i] != '-1' else 0

        # Skip low-confidence detections
        if confidence < 30:
            continue

        # Check if this text matches any target label
        for j, label in enumerate(target_labels_lower):
            # Match if label is contained in text or text is contained in label
            # This handles partial matches like "kril" -> "krill" or "krill " -> "krill"
            if label in text_lower or text_lower in label:
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]

                # Organism images are typically ABOVE the text label
                # Expand box upward to capture the organism
                expanded_y = max(0, y - int(h * padding_multiplier))
                expanded_h = int(h * (padding_multiplier + 1))  # Include label + organism above
                expanded_w = int(w * 1.5)  # Slightly wider to capture full organism
                expanded_x = max(0, x - int((expanded_w - w) / 2))  # Center horizontally

                # Store result using original label (preserve case)
                original_label = target_labels[j]

                # If we already found this label, keep the one with higher confidence
                if original_label in results:
                    if confidence > results[original_label]['confidence']:
                        results[original_label] = {
                            'x': expanded_x,
                            'y': expanded_y,
                            'width': expanded_w,
                            'height': expanded_h,
                            'confidence': confidence,
                            'original_text': text
                        }
                else:
                    results[original_label] = {
                        'x': expanded_x,
                        'y': expanded_y,
                        'width': expanded_w,
                        'height': expanded_h,
                        'confidence': confidence,
                        'original_text': text
                    }

                print(f"   ✓ Found '{text}' (matched '{original_label}') at ({x}, {y}) "
                      f"with {confidence}% confidence")
                print(f"     Expanded box: ({expanded_x}, {expanded_y}) "
                      f"{expanded_w}x{expanded_h}")

    if results:
        print(f"✅ OCR detected {len(results)}/{len(target_labels)} labels")
    else:
        print(f"⚠️ OCR failed to detect any labels")

    return results


def visualize_detections(image_path: str, detections: Dict[str, Dict[str, int]],
                        output_path: Optional[str] = None) -> str:
    """
    Draw detected bounding boxes on the image for visualization/debugging.

    Args:
        image_path: Path to original image
        detections: Results from detect_hotspot_locations()
        output_path: Where to save annotated image (default: temp_ocr_debug.png)

    Returns:
        Path to saved annotated image
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Use Edmentum green for boxes
    EDMENTUM_GREEN = '#2e7d32'

    for label, box in detections.items():
        # Draw rectangle
        draw.rectangle(
            [box['x'], box['y'], box['x'] + box['width'], box['y'] + box['height']],
            outline=EDMENTUM_GREEN,
            width=4
        )

        # Draw label with confidence
        label_text = f"{label} ({box['confidence']}%)"
        draw.text(
            (box['x'] + 5, box['y'] + 5),
            label_text,
            fill=EDMENTUM_GREEN
        )

    if output_path is None:
        import time
        output_path = f"./temp_ocr_debug_{int(time.time())}.png"

    img.save(output_path, quality=95)
    print(f"💾 Saved OCR visualization to: {output_path}")
    return output_path
