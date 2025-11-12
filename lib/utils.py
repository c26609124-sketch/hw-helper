"""
HW Helper Utility Library
==========================
Consolidated module combining:
- response_validator.py: Validates and auto-fixes AI responses
- visual_element_detector.py: Identifies and extracts interactive regions from screenshots
- progressive_json_parser.py: Parses streaming JSON progressively
- ui_export.py: Exports CustomTkinter widget trees to JSON

This module provides utilities for response validation, visual element detection,
progressive JSON parsing, and UI widget tree export.
"""

import json
import re
import tkinter
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFilter


# ============================================================================
# RESPONSE VALIDATOR
# ============================================================================

class ResponseValidator:
    """Validates and fixes AI response data"""

    def __init__(self):
        self.validation_warnings = []

    def validate_and_fix(self, response_data: Dict) -> Dict:
        """
        Main validation and auto-fix method

        Args:
            response_data: AI response dict with answers array

        Returns:
            Fixed response_data dict
        """
        self.validation_warnings = []

        if not isinstance(response_data, dict):
            print("⚠️ Validator: Response is not a dict")
            return response_data

        answers = response_data.get('answers', [])
        if not answers:
            print("⚠️ Validator: No answers found")
            return response_data

        # Determine question type
        question_type = response_data.get('metadata', {}).get('question_type', 'unknown')
        if not question_type:
            question_type = response_data.get('initial_analysis', {}).get('question_type', 'unknown')

        print(f"🔍 Validating response for question_type: {question_type}")

        # Apply type-specific validation
        if question_type == 'multiple_choice':
            fixed_answers = self._validate_multiple_choice(answers)
            response_data['answers'] = fixed_answers
        elif question_type == 'matching_pair':
            fixed_answers = self._validate_matching_pairs(answers)
            response_data['answers'] = fixed_answers

        # Display warnings if any
        if self.validation_warnings:
            print("⚠️ VALIDATION WARNINGS:")
            for warning in self.validation_warnings:
                print(f"   • {warning}")

        return response_data

    def _validate_multiple_choice(self, answers: List[Dict]) -> List[Dict]:
        """Validate and fix multiple choice answers"""
        mc_answers = [a for a in answers if a.get('content_type') == 'multiple_choice_option']

        if not mc_answers:
            return answers

        print(f"   Found {len(mc_answers)} multiple choice options")

        # Check how many are marked correct
        correct_count = sum(1 for a in mc_answers if a.get('is_correct_option', False))

        if correct_count == 0:
            # NO correct answer marked - select highest confidence
            self.validation_warnings.append(
                f"NO answer marked as correct! Auto-selecting highest confidence answer."
            )
            mc_answers = self._auto_select_correct_answer(mc_answers)

        elif correct_count > 1:
            # MULTIPLE correct answers marked - keep only highest confidence
            self.validation_warnings.append(
                f"MULTIPLE answers marked as correct ({correct_count})! Auto-selecting highest confidence."
            )
            mc_answers = self._auto_select_correct_answer(mc_answers, force=True)

        else:
            print(f"   ✓ Exactly 1 answer marked as correct")

        # Ensure unique and proper labels
        mc_answers = self._fix_labels(mc_answers)

        # Check for duplicate content
        mc_answers = self._check_duplicate_content(mc_answers)

        # Adjust confidence scoring
        mc_answers = self._adjust_confidence(mc_answers)

        # Replace mc_answers in original answers array
        fixed_answers = []
        mc_index = 0
        for answer in answers:
            if answer.get('content_type') == 'multiple_choice_option':
                fixed_answers.append(mc_answers[mc_index])
                mc_index += 1
            else:
                fixed_answers.append(answer)

        return fixed_answers

    def _auto_select_correct_answer(self, mc_answers: List[Dict], force: bool = False) -> List[Dict]:
        """Auto-select the correct answer based on highest confidence"""
        if force:
            # Clear all correct flags first
            for answer in mc_answers:
                answer['is_correct_option'] = False

        # Find highest confidence answer
        max_confidence = -1
        max_index = 0

        for i, answer in enumerate(mc_answers):
            confidence = answer.get('confidence', 0.0)
            if isinstance(confidence, (int, float)) and confidence > max_confidence:
                max_confidence = confidence
                max_index = i

        # Mark the highest confidence answer as correct
        mc_answers[max_index]['is_correct_option'] = True

        correct_letter = mc_answers[max_index].get('label', '?')
        print(f"   → Auto-selected answer {correct_letter} (confidence: {max_confidence:.2f})")

        return mc_answers

    def _fix_labels(self, mc_answers: List[Dict]) -> List[Dict]:
        """Ensure each answer has a unique label (A, B, C, D, E, F...)"""
        expected_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        # Extract current labels
        current_labels = []
        for answer in mc_answers:
            label = answer.get('label', '')
            # Try to extract from answer_id if label is missing
            if not label:
                answer_id = answer.get('answer_id', '')
                if '_' in answer_id:
                    parts = answer_id.split('_')
                    last_part = parts[-1]
                    if len(last_part) == 1 and last_part.isalpha():
                        label = last_part.upper()
            current_labels.append(label)

        # Check for issues
        has_duplicates = len(current_labels) != len(set(current_labels))
        has_missing = '' in current_labels

        if has_duplicates or has_missing:
            self.validation_warnings.append(
                f"Label issues detected (duplicates: {has_duplicates}, missing: {has_missing}). Auto-assigning A, B, C, D..."
            )

            # Reassign labels
            for i, answer in enumerate(mc_answers):
                if i < len(expected_labels):
                    new_label = expected_labels[i]
                    answer['label'] = new_label
                    # Update answer_id if needed
                    if 'answer_id' not in answer or not answer['answer_id']:
                        answer['answer_id'] = f'mc_option_{new_label}'
                    print(f"   → Assigned label '{new_label}' to option {i+1}")
        else:
            print(f"   ✓ All labels unique and present: {', '.join(current_labels)}")

        return mc_answers

    def _check_duplicate_content(self, mc_answers: List[Dict]) -> List[Dict]:
        """Check if multiple answers have the same text content"""
        content_list = [a.get('text_content', '').strip() for a in mc_answers]

        # Check for duplicates
        unique_content = set(content_list)
        if len(unique_content) < len(content_list):
            # Found duplicates
            duplicate_content = [c for c in content_list if content_list.count(c) > 1]
            self.validation_warnings.append(
                f"DUPLICATE content detected! Multiple options have same text: '{duplicate_content[0][:50]}...'"
            )
            print(f"   ⚠️ Duplicate content: {duplicate_content[0][:80]}")

        return mc_answers

    def _adjust_confidence(self, mc_answers: List[Dict]) -> List[Dict]:
        """Adjust confidence scores to be more meaningful"""
        # Find the correct answer
        correct_index = None
        for i, answer in enumerate(mc_answers):
            if answer.get('is_correct_option', False):
                correct_index = i
                break

        if correct_index is None:
            return mc_answers

        # Get current confidences
        confidences = [a.get('confidence', 0.5) for a in mc_answers]

        # Check if all confidences are too similar
        if max(confidences) - min(confidences) < 0.1:
            self.validation_warnings.append(
                f"All confidence scores too similar ({min(confidences):.2f}-{max(confidences):.2f}). Adjusting..."
            )

            # Boost correct answer confidence
            mc_answers[correct_index]['confidence'] = 0.95

            # Lower incorrect answer confidences
            for i, answer in enumerate(mc_answers):
                if i != correct_index:
                    answer['confidence'] = 0.2 + (i * 0.1)

            print(f"   → Adjusted confidences: Correct={mc_answers[correct_index]['confidence']:.2f}, Others={[a['confidence'] for i, a in enumerate(mc_answers) if i != correct_index]}")

        return mc_answers

    def _validate_matching_pairs(self, answers: List[Dict]) -> List[Dict]:
        """Validate matching pair answers"""
        pair_answers = [a for a in answers if a.get('content_type') == 'matching_pair']

        if not pair_answers:
            return answers

        print(f"   Found {len(pair_answers)} matching pairs")

        for i, pair in enumerate(pair_answers):
            pair_data = pair.get('pair_data', {})
            term = pair_data.get('term', '')
            match = pair_data.get('match', pair_data.get('match_value', ''))

            if not term or not match:
                self.validation_warnings.append(
                    f"Pair {i+1} missing term or match! Term: '{term}', Match: '{match}'"
                )

        # Check for duplicate terms
        terms = [p.get('pair_data', {}).get('term', '') for p in pair_answers]
        if len(terms) != len(set(terms)):
            self.validation_warnings.append("Duplicate terms detected in matching pairs")

        # Check for duplicate matches
        matches = [p.get('pair_data', {}).get('match', p.get('pair_data', {}).get('match_value', '')) for p in pair_answers]
        if len(matches) != len(set(matches)):
            self.validation_warnings.append("Duplicate matches detected in matching pairs")

        return answers

    def get_warnings(self) -> List[str]:
        """Get list of validation warnings"""
        return self.validation_warnings


def validate_response(response_data: Dict) -> Tuple[Dict, List[str]]:
    """
    Validate and fix AI response

    Args:
        response_data: AI response dict

    Returns:
        (fixed_response_data, list_of_warnings)
    """
    validator = ResponseValidator()
    fixed_data = validator.validate_and_fix(response_data)
    warnings = validator.get_warnings()
    return fixed_data, warnings


# ============================================================================
# VISUAL ELEMENT DETECTOR
# ============================================================================

class VisualElementDetector:
    """Detects and extracts visual elements from homework screenshots"""

    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size
        self.detected_regions = []

    def detect_grid_boxes(self, min_box_size: int = 50,
                         grid_rows: Optional[int] = None,
                         grid_cols: Optional[int] = None) -> List[Dict]:
        """Detect grid-based visual boxes using edge detection and contour analysis"""
        # Convert to numpy array for processing
        img_array = np.array(self.image.convert('L'))  # Grayscale

        # Apply edge detection
        edges = self._detect_edges_simple(img_array)

        # Find rectangular regions
        regions = self._find_rectangular_regions(edges, min_box_size)

        # If grid parameters provided, try to organize into grid
        if grid_rows and grid_cols:
            regions = self._organize_into_grid(regions, grid_rows, grid_cols)

        self.detected_regions = regions
        return regions

    def detect_standard_question_layout(self) -> Dict:
        """Detect common question layout patterns"""
        layout = {
            "visual_area": None,
            "text_options_area": None,
            "submit_button_area": None,
            "full_question_area": None
        }

        # Heuristic: Top 60% is usually visual area
        visual_height = int(self.height * 0.6)
        layout["visual_area"] = {
            "x1": 0, "y1": 0,
            "x2": self.width, "y2": visual_height,
            "type": "visual_grid"
        }

        # Bottom 35% for text options
        text_start = visual_height
        text_end = int(self.height * 0.95)
        layout["text_options_area"] = {
            "x1": 0, "y1": text_start,
            "x2": self.width, "y2": text_end,
            "type": "text_options"
        }

        # Bottom 5% for submit button
        layout["submit_button_area"] = {
            "x1": 0, "y1": text_end,
            "x2": self.width, "y2": self.height,
            "type": "submit"
        }

        layout["full_question_area"] = {
            "x1": 0, "y1": 0,
            "x2": self.width, "y2": self.height,
            "type": "full"
        }

        return layout

    def extract_region(self, x1: int, y1: int, x2: int, y2: int,
                      output_path: Optional[str] = None) -> Image.Image:
        """Extract a sub-region from the image"""
        region = self.image.crop((x1, y1, x2, y2))

        if output_path:
            region.save(output_path)

        return region

    def extract_visual_boxes_from_grid(self, num_boxes: int = 6,
                                      grid_layout: str = "2x3",
                                      padding: int = 10) -> List[Dict]:
        """Extract individual visual boxes from a detected grid"""
        layout = self.detect_standard_question_layout()
        visual_area = layout["visual_area"]

        rows, cols = map(int, grid_layout.split('x'))

        va_x1, va_y1 = visual_area["x1"], visual_area["y1"]
        va_x2, va_y2 = visual_area["x2"], visual_area["y2"]
        va_width = va_x2 - va_x1
        va_height = va_y2 - va_y1

        box_width = va_width // cols
        box_height = va_height // rows

        boxes = []
        box_id = 0

        for row in range(rows):
            for col in range(cols):
                if box_id >= num_boxes:
                    break

                # Calculate box boundaries
                x1 = va_x1 + (col * box_width) + (col * 35)
                y1 = va_y1 + (row * box_height) + (row * 55)
                x2 = x1 + 115
                y2 = y1 + 105

                # Ensure coordinates are within image bounds
                x1 = max(0, min(x1, self.width))
                y1 = max(0, min(y1, self.height))
                x2 = max(0, min(x2, self.width))
                y2 = max(0, min(y2, self.height))

                # Only create box if it has valid dimensions
                if x2 > x1 + 20 and y2 > y1 + 20:
                    box_info = {
                        "id": f"box_{box_id}",
                        "row": row,
                        "col": col,
                        "coordinates": {
                            "x1": x1, "y1": y1,
                            "x2": x2, "y2": y2
                        },
                        "center": {
                            "x": (x1 + x2) // 2,
                            "y": (y1 + y2) // 2
                        },
                        "width": x2 - x1,
                        "height": y2 - y1
                    }

                    boxes.append(box_info)
                    box_id += 1

        return boxes

    def create_annotated_image(self, boxes: List[Dict],
                              output_path: str = "annotated_screenshot.png",
                              show_labels: bool = True) -> Image.Image:
        """Create an annotated version of the image showing detected boxes"""
        annotated = self.image.copy()
        draw = ImageDraw.Draw(annotated)

        for box in boxes:
            coords = box["coordinates"]
            x1, y1 = coords["x1"], coords["y1"]
            x2, y2 = coords["x2"], coords["y2"]

            # Draw rectangle
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

            if show_labels:
                # Draw label
                label = box.get("id", "?")
                draw.text((x1 + 5, y1 + 5), label, fill="red")

        annotated.save(output_path)
        return annotated

    def save_box_metadata(self, boxes: List[Dict], output_path: str = "boxes_metadata.json"):
        """Save detected box metadata to JSON file"""
        metadata = {
            "image_path": self.image_path,
            "image_size": {"width": self.width, "height": self.height},
            "boxes": boxes,
            "total_boxes": len(boxes)
        }

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata

    # Helper methods
    def _detect_edges_simple(self, img_array: np.ndarray, threshold: int = 128) -> np.ndarray:
        """Simple edge detection using threshold"""
        edges = np.zeros_like(img_array)
        edges[img_array > threshold] = 255
        return edges

    def _find_rectangular_regions(self, edges: np.ndarray, min_size: int) -> List[Dict]:
        """Find rectangular regions in edge image"""
        # Simplified region detection
        regions = []
        return regions

    def _organize_into_grid(self, regions: List[Dict], rows: int, cols: int) -> List[Dict]:
        """Organize detected regions into a grid structure"""
        # Placeholder implementation
        return regions


def analyze_drag_to_image_question(image_path: str,
                                   grid_layout: str = "2x3",
                                   num_boxes: int = 6) -> Dict:
    """Analyze a drag-to-image question and extract visual elements"""
    detector = VisualElementDetector(image_path)

    # Detect overall layout
    layout = detector.detect_standard_question_layout()

    # Extract visual boxes
    boxes = detector.extract_visual_boxes_from_grid(
        num_boxes=num_boxes,
        grid_layout=grid_layout,
        padding=15
    )

    # Create annotated image for visualization
    annotated_image_path = image_path.replace(".png", "_annotated.png")
    detector.create_annotated_image(boxes, annotated_image_path)

    # Save metadata
    metadata_path = image_path.replace(".png", "_boxes_metadata.json")
    metadata = detector.save_box_metadata(boxes, metadata_path)

    return {
        "layout": layout,
        "boxes": boxes,
        "metadata": metadata,
        "annotated_image_path": annotated_image_path,
        "original_image_size": {"width": detector.width, "height": detector.height}
    }


# ============================================================================
# PROGRESSIVE JSON PARSER
# ============================================================================

class ProgressiveJSONParser:
    """
    Parses streaming JSON and extracts complete objects as they arrive
    Handles incomplete/malformed JSON gracefully
    """

    def __init__(self):
        self.buffer = ""
        self.parsed_data = {
            "initial_analysis": None,
            "metadata": None,
            "identified_question": None,
            "answers": [],
            "status": None
        }
        self.last_rendered_answer_count = 0
        self.initial_analysis_extracted = False
        self.metadata_extracted = False

    def add_chunk(self, chunk: str) -> Tuple[bool, Dict]:
        """
        Add a chunk of JSON text and attempt to parse

        Returns:
            (has_new_content, extracted_data)
        """
        self.buffer += chunk

        # Try to parse the buffer
        newly_complete = {}

        # Try full parse first
        try:
            full_data = json.loads(self.buffer)
            # Successfully parsed complete JSON!
            self.parsed_data = full_data
            newly_complete = {
                "complete": True,
                "data": full_data
            }
            return (True, newly_complete)
        except json.JSONDecodeError:
            # Not complete yet, try partial extraction
            pass

        # PRIORITY 0: Extract initial_analysis FIRST
        if not self.initial_analysis_extracted:
            initial_analysis = self._extract_initial_analysis(self.buffer)
            if initial_analysis:
                self.parsed_data["initial_analysis"] = initial_analysis
                self.initial_analysis_extracted = True
                newly_complete["initial_analysis"] = initial_analysis
                print(f"   🔍 Initial analysis extracted: {initial_analysis.get('edmentum_type_name', 'unknown')} with strategy {initial_analysis.get('rendering_strategy', 'unknown')}")

        # PRIORITY 1: Extract metadata
        if not self.metadata_extracted:
            metadata = self._extract_metadata(self.buffer)
            if metadata:
                self.parsed_data["metadata"] = metadata
                self.metadata_extracted = True
                newly_complete["metadata"] = metadata
                print(f"   📋 Metadata extracted: {metadata.get('question_type', 'unknown')} with {metadata.get('total_answers', 0)} answers")

        # Extract identified_question if complete
        if not self.parsed_data.get("identified_question"):
            question = self._extract_field(self.buffer, "identified_question")
            if question:
                self.parsed_data["identified_question"] = question
                newly_complete["identified_question"] = question

        # Extract complete answer objects
        new_answers = self._extract_complete_answers(self.buffer)
        if len(new_answers) > self.last_rendered_answer_count:
            # We have new complete answers!
            newly_complete["new_answers"] = new_answers[self.last_rendered_answer_count:]
            self.last_rendered_answer_count = len(new_answers)

        has_new = len(newly_complete) > 0
        return (has_new, newly_complete)

    def _extract_field(self, json_str: str, field_name: str) -> Optional[str]:
        """Extract a complete string field value if available"""
        pattern = rf'"{field_name}"\s*:\s*"([^"]*)"'
        match = re.search(pattern, json_str)
        if match:
            return match.group(1)
        return None

    def _extract_complete_answers(self, json_str: str) -> List[Dict]:
        """Extract complete answer objects from partial JSON"""
        answers = []

        # Find the answers array start
        answers_start = json_str.find('"answers":')
        if answers_start == -1:
            return answers

        # Extract everything after "answers": [
        after_answers = json_str[answers_start:]
        array_start = after_answers.find('[')
        if array_start == -1:
            return answers

        # Find complete objects by counting braces
        search_from = array_start + 1
        while True:
            # Find next object start
            obj_start = after_answers.find('{', search_from)
            if obj_start == -1:
                break

            # Count braces to find matching close
            brace_count = 0
            obj_end = -1
            for i in range(obj_start, len(after_answers)):
                if after_answers[i] == '{':
                    brace_count += 1
                elif after_answers[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        obj_end = i + 1
                        break

            if obj_end > obj_start:
                # Found complete object
                obj_str = after_answers[obj_start:obj_end]
                try:
                    obj_data = json.loads(obj_str)
                    answers.append(obj_data)
                    search_from = obj_end
                except json.JSONDecodeError:
                    # Not actually complete, continue
                    search_from = obj_start + 1
            else:
                # No complete object found
                break

        return answers

    def _extract_metadata(self, json_str: str) -> Optional[Dict]:
        """Extract complete metadata object if available"""
        # Find the metadata field
        metadata_start = json_str.find('"metadata"')
        if metadata_start == -1:
            return None

        # Find the start of the metadata object
        after_metadata = json_str[metadata_start:]
        colon_pos = after_metadata.find(':')
        if colon_pos == -1:
            return None

        # Find the opening brace
        obj_start = after_metadata.find('{', colon_pos)
        if obj_start == -1:
            return None

        # Count braces to find complete object
        brace_count = 0
        obj_end = -1
        for i in range(obj_start, len(after_metadata)):
            if after_metadata[i] == '{':
                brace_count += 1
            elif after_metadata[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    obj_end = i + 1
                    break

        if obj_end > obj_start:
            # Found complete metadata object
            obj_str = after_metadata[obj_start:obj_end]
            try:
                metadata = json.loads(obj_str)
                return metadata
            except json.JSONDecodeError:
                return None

        return None

    def _extract_initial_analysis(self, json_str: str) -> Optional[Dict]:
        """Extract complete initial_analysis object if available"""
        # Find the initial_analysis field
        analysis_start = json_str.find('"initial_analysis"')
        if analysis_start == -1:
            return None

        # Find the start of the initial_analysis object
        after_analysis = json_str[analysis_start:]
        colon_pos = after_analysis.find(':')
        if colon_pos == -1:
            return None

        # Find the opening brace
        obj_start = after_analysis.find('{', colon_pos)
        if obj_start == -1:
            return None

        # Count braces to find complete object
        brace_count = 0
        obj_end = -1
        for i in range(obj_start, len(after_analysis)):
            if after_analysis[i] == '{':
                brace_count += 1
            elif after_analysis[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    obj_end = i + 1
                    break

        if obj_end > obj_start:
            # Found complete initial_analysis object
            obj_str = after_analysis[obj_start:obj_end]
            try:
                initial_analysis = json.loads(obj_str)
                return initial_analysis
            except json.JSONDecodeError:
                return None

        return None

    def get_current_state(self) -> Dict:
        """Get currently parsed data"""
        return self.parsed_data


# ============================================================================
# UI EXPORT (Widget Tree Export)
# ============================================================================

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


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Response Validator
    'ResponseValidator',
    'validate_response',

    # Visual Element Detector
    'VisualElementDetector',
    'analyze_drag_to_image_question',

    # Progressive JSON Parser
    'ProgressiveJSONParser',

    # UI Export
    'export_widget_tree',
    'get_widget_summary',
]
