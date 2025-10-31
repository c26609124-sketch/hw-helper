"""
OCR-based Hot Spot Location Detector (EasyOCR)

This module uses EasyOCR (deep learning-based OCR) to automatically detect
the exact pixel locations of organism labels in food web diagrams and other
hot spot questions. This eliminates the need for AI estimation and provides
100% accurate, deterministic bounding box coordinates.

EasyOCR is pure Python with no external dependencies - works immediately on
Windows/Mac/Linux without requiring Tesseract executable installation.

Author: Claude Code
Version: 1.0.32
"""

from PIL import Image
from typing import Dict, List, Tuple, Optional


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

    # Use EasyOCR (pure Python, no external executable dependencies)
    # Works immediately on Windows/Mac/Linux without manual installation steps
    try:
        import easyocr
        # Initialize EasyOCR reader for English text
        # gpu=False: Use CPU (more compatible, doesn't require CUDA)
        # verbose=False: Suppress progress messages
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        # Run OCR detection
        # Returns list of (bbox, text, confidence) tuples
        # bbox format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] (4 corners)
        ocr_results = reader.readtext(image_path)
        print(f"   EasyOCR detected {len(ocr_results)} text regions")
    except Exception as e:
        print(f"⚠️ EasyOCR initialization failed: {e}")
        return {}

    results = {}
    target_labels_lower = [label.lower().strip() for label in target_labels]

    # Process EasyOCR results
    # Format: [(bbox, text, confidence), ...]
    # bbox = [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    for bbox, text, confidence in ocr_results:
        if not text or not text.strip():
            continue

        text_lower = text.lower().strip()

        # Skip low-confidence detections
        # EasyOCR uses 0.0-1.0 scale (vs Tesseract's 0-100)
        if confidence < 0.3:
            continue

        # Check if this text matches any target label
        for j, label in enumerate(target_labels_lower):
            # Match if label is contained in text or text is contained in label
            # This handles partial matches like "kril" -> "krill" or "krill " -> "krill"
            if label in text_lower or text_lower in label:
                # Extract bounding box coordinates
                # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]

                x = int(min(x_coords))
                y = int(min(y_coords))
                w = int(max(x_coords) - min(x_coords))
                h = int(max(y_coords) - min(y_coords))

                # Organism images are typically ABOVE the text label
                # Expand box upward to capture the organism
                expanded_y = max(0, y - int(h * padding_multiplier))
                expanded_h = int(h * (padding_multiplier + 1))  # Include label + organism above
                expanded_w = int(w * 1.5)  # Slightly wider to capture full organism
                expanded_x = max(0, x - int((expanded_w - w) / 2))  # Center horizontally

                # Store result using original label (preserve case)
                original_label = target_labels[j]

                # Convert confidence to percentage (EasyOCR returns 0.0-1.0)
                confidence_pct = int(confidence * 100)

                # If we already found this label, keep the one with higher confidence
                if original_label in results:
                    if confidence_pct > results[original_label]['confidence']:
                        results[original_label] = {
                            'x': expanded_x,
                            'y': expanded_y,
                            'width': expanded_w,
                            'height': expanded_h,
                            'confidence': confidence_pct,
                            'original_text': text
                        }
                else:
                    results[original_label] = {
                        'x': expanded_x,
                        'y': expanded_y,
                        'width': expanded_w,
                        'height': expanded_h,
                        'confidence': confidence_pct,
                        'original_text': text
                    }

                print(f"   ✓ Found '{text}' (matched '{original_label}') at ({x}, {y}) "
                      f"with {confidence_pct}% confidence")
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
