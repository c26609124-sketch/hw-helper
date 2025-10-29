"""
Enhanced Answer Display - Creates visual representations of AI answers
Supports drag-to-image matching questions with coordinate-based rendering
"""

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps
from typing import Dict, List, Optional, Tuple
import os
import traceback


class DragToImageRenderer:
    """Renders drag-to-image matching questions with visual connections"""
    
    def __init__(self, parent_frame: ctk.CTkFrame, image_path: str):
        self.parent_frame = parent_frame
        self.image_path = image_path
        try:
            self.original_image = Image.open(image_path)
            self.img_width, self.img_height = self.original_image.size
        except Exception as e:
            print(f"Error loading image in DragToImageRenderer: {e}")
            raise
        
    def create_visual_matching_display(self, 
                                      matching_answers: List[Dict],
                                      grid_layout: str = "2x3") -> ctk.CTkFrame:
        """
        Create a visual display showing matches between draggable items and visual boxes
        
        Args:
            matching_answers: List of matching_pair answer objects from AI
            grid_layout: Grid layout as "rows x cols"
            
        Returns:
            CTkFrame with the visual matching display
        """
        # Create main container
        container = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        
        # Title section
        title_frame = ctk.CTkFrame(container, fg_color=("gray90", "gray20"), corner_radius=6)
        title_frame.pack(fill="x", pady=(5, 10), padx=10)
        
        ctk.CTkLabel(
            title_frame,
            text="Drag-to-Image Matching Question",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=5, padx=10, anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Drag each tile to the correct location on the image.",
            font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"),
            text_color=("gray50", "gray60")
        ).pack(pady=(0, 5), padx=10, anchor="w")
        
        # Detect and extract boxes
        try:
            rows, cols = map(int, grid_layout.split('x'))
            boxes = self._extract_grid_boxes(rows, cols)
            
            if not boxes:
                raise ValueError("No boxes detected")
            
            print(f"Extracted {len(boxes)} visual boxes from grid")
            
            # Create visual grid display
            grid_frame = ctk.CTkFrame(container, fg_color=("gray95", "gray15"), corner_radius=8)
            grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Configure grid
            for r in range(rows):
                grid_frame.grid_rowconfigure(r, weight=1)
            for c in range(cols):
                grid_frame.grid_columnconfigure(c, weight=1)
            
            # Map matching answers to boxes
            box_to_answer_map = self._map_answers_to_boxes(boxes, matching_answers)
            
            # Display boxes with extracted images and matched text
            for idx, box in enumerate(boxes):
                if idx >= len(boxes):
                    break
                    
                # Get matched answer for this box
                matched_answer = box_to_answer_map.get(idx)
                
                box_container = self._create_box_widget(
                    grid_frame, 
                    box, 
                    idx,
                    matched_answer
                )
                
                row = idx // cols
                col = idx % cols
                box_container.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        except Exception as e:
            print(f"Error creating grid display: {e}")
            traceback.print_exc()
            # Show error in container
            ctk.CTkLabel(
                container,
                text=f"Error rendering visual grid: {str(e)}",
                text_color="red"
            ).pack(pady=20, padx=10)
        
        # Display matches summary below
        matches_frame = ctk.CTkFrame(container, fg_color="transparent")
        matches_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            matches_frame,
            text="AI-Detected Matches:",
            font=ctk.CTkFont(weight="bold", size=12)
        ).pack(anchor="w", pady=(0, 5))
        
        for idx, match in enumerate(matching_answers):
            self._create_match_item(matches_frame, match, idx + 1)
        
        return container
    
    def _extract_grid_boxes(self, rows: int, cols: int) -> List[Dict]:
        """
        Extract visual boxes using HARDCODED coordinates for pixel-perfect accuracy
        
        Based on manual analysis of Edmentum/Plato screenshot structure:
        - Image size: 1110x1141px (typical captured iframe)
        - Grid contained in white content box
        - 2 rows × 3 columns of visual elements
        - Each cell has a visual + small text label below it
        
        This uses absolute coordinates that work for this specific layout.
        For other platforms, use manual_coordinate_tool.py to measure.
        """
        
        # HARDCODED PRECISE COORDINATES for 1110x1141 image
        # Based on actual visual analysis of the screenshot structure
        
        # The grid structure in the screenshot:
        # Top row Y: ~175 to ~310 (visual only, excluding labels)
        # Bottom row Y: ~335 to ~470 (visual only, excluding labels)
        # Columns are evenly spaced within content box
        
        # PIXEL-PERFECT coordinates for 2x3 grid
        if rows == 2 and cols == 3:
            # Ultra-precise hardcoded boxes - REFINED to exclude visible cell borders
            # Coordinates adjusted after visual inspection showed border artifacts
            hardcoded_boxes_coords = [
                # Row 1 - Top row of visual elements
                (250, 180, 356, 276),  # Box 1: Pie chart (106x96px)
                (400, 180, 506, 276),  # Box 2: China map (106x96px)
                (550, 180, 653, 276),  # Box 3: Empire State Building (103x96px) - tighter right edge
                # Row 2 - Bottom row of visual elements
                (250, 340, 356, 436),  # Box 4: Text comparison (106x96px)
                (400, 340, 506, 436),  # Box 5: Football diagram (106x96px)
                (550, 340, 653, 436),  # Box 6: Venn/circles diagram (103x96px) - tighter right edge
            ]
            
            boxes = []
            for idx, (x1, y1, x2, y2) in enumerate(hardcoded_boxes_coords):
                try:
                    # Ensure coordinates within bounds
                    x1 = max(0, min(x1, self.img_width))
                    y1 = max(0, min(y1, self.img_height))
                    x2 = max(0, min(x2, self.img_width))
                    y2 = max(0, min(y2, self.img_height))
                    
                    if x2 > x1 and y2 > y1:
                        box_image = self.original_image.crop((x1, y1, x2, y2))
                        
                        row = idx // cols
                        col = idx % cols
                        
                        box_info = {
                            "id": f"visual_{row}_{col}",
                            "index": idx,
                            "row": row,
                            "col": col,
                            "coordinates": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                            "image": box_image,
                            "matched_text": None,
                            "size": {"width": x2 - x1, "height": y2 - y1}
                        }
                        boxes.append(box_info)
                        print(f"Box {idx+1}: {box_info['size']['width']}x{box_info['size']['height']}px at ({x1},{y1})")
                except Exception as e:
                    print(f"Warning: Could not extract hardcoded box {idx+1}: {e}")
                    continue
            
            if boxes:
                return boxes
        
        # FALLBACK: Use percentage-based calculation for other grid sizes
        # or if hardcoded coordinates don't work
        print(f"Using fallback percentage-based coordinates for {rows}x{cols} grid")
        
        boxes = []
        visual_start_y = int(self.img_height * 0.155)
        visual_end_y = int(self.img_height * 0.415)
        visual_height = visual_end_y - visual_start_y
        
        left_margin = int(self.img_width * 0.215)
        right_margin = int(self.img_width * 0.405)
        visual_width = self.img_width - left_margin - right_margin
        
        box_width = visual_width // cols
        box_height = visual_height // rows
        
        for row in range(rows):
            for col in range(cols):
                x1 = left_margin + (col * box_width) + (col * 35)  # Add inter-box spacing
                y1 = visual_start_y + (row * box_height) + (row * 55)
                x2 = x1 + 115  # Fixed width
                y2 = y1 + 105  # Fixed height
                
                # Ensure coordinates are within image bounds
                x1 = max(0, min(x1, self.img_width))
                y1 = max(0, min(y1, self.img_height))
                x2 = max(0, min(x2, self.img_width))
                y2 = max(0, min(y2, self.img_height))
                
                # Only create box if it has valid dimensions
                if x2 > x1 + 20 and y2 > y1 + 20:  # Minimum 20px in each dimension
                    try:
                        # Extract sub-image
                        box_image = self.original_image.crop((x1, y1, x2, y2))
                        
                        box_info = {
                            "id": f"visual_{row}_{col}",
                            "index": row * cols + col,
                            "row": row,
                            "col": col,
                            "coordinates": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                            "image": box_image,
                            "matched_text": None,
                            "size": {"width": x2 - x1, "height": y2 - y1}
                        }
                        
                        boxes.append(box_info)
                        print(f"Box {len(boxes)}: {box_info['size']}")
                    except Exception as e:
                        print(f"Warning: Could not extract box at row={row}, col={col}: {e}")
                        continue
        
        return boxes
    
    def _map_answers_to_boxes(self, boxes: List[Dict], matching_answers: List[Dict]) -> Dict[int, Dict]:
        """
        Map matching answers to box indices
        
        For drag-to-image questions, the 'term' field usually contains a description
        of what's in the visual box, and 'match' contains what should be dragged to it.
        
        Args:
            boxes: List of detected visual boxes
            matching_answers: List of matching_pair answers from AI
            
        Returns:
            Dictionary mapping box index to answer dict
        """
        box_map = {}
        
        # Simple sequential mapping for now
        # In a more advanced version, could use image similarity or text analysis
        for idx, answer in enumerate(matching_answers):
            if idx < len(boxes):
                box_map[idx] = answer
        
        return box_map
    
    def _create_box_widget(self, parent, box: Dict, idx: int, 
                          matched_answer: Optional[Dict]) -> ctk.CTkFrame:
        """Create a widget for a single visual box with its matched content"""
        # Determine if this box has a match
        has_match = matched_answer is not None
        
        # Color scheme based on match status
        if has_match:
            bg_color = ("white", "gray28")
            border_color = ("#4CAF50", "#388E3C")  # Green for matched
            border_width = 2
        else:
            bg_color = ("white", "gray25")
            border_color = ("gray70", "gray40")
            border_width = 1
        
        container = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            border_width=border_width,
            border_color=border_color,
            corner_radius=8
        )
        
        # Display the extracted image
        box_image = box["image"]
        
        # Resize for display (max dimensions while maintaining aspect ratio)
        max_width, max_height = 180, 140
        box_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        ctk_image = ctk.CTkImage(
            light_image=box_image,
            dark_image=box_image,
            size=box_image.size
        )
        
        image_label = ctk.CTkLabel(container, image=ctk_image, text="")
        image_label.image = ctk_image  # Keep reference
        image_label.pack(pady=8, padx=8)
        
        # Display matched text if found
        if has_match and matched_answer:
            pair_data = matched_answer.get("pair_data", {})
            match_text = pair_data.get("match", "")
            confidence = matched_answer.get("confidence", 0)
            
            if match_text:
                # Create dragged text simulation
                dragged_text_frame = ctk.CTkFrame(
                    container,
                    fg_color=("#E8F5E9", "#1A3A1A"),
                    corner_radius=6,
                    border_width=1,
                    border_color=("#4CAF50", "#2E7D32")
                )
                dragged_text_frame.pack(pady=(0, 8), padx=8, fill="x")
                
                # Checkmark + text
                match_display = ctk.CTkLabel(
                    dragged_text_frame,
                    text=f"✓ {match_text}",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    wraplength=160,
                    anchor="center"
                )
                match_display.pack(pady=6, padx=6)
                
                # Confidence indicator
                if confidence > 0:
                    conf_label = ctk.CTkLabel(
                        dragged_text_frame,
                        text=f"{confidence*100:.0f}% confident",
                        font=ctk.CTkFont(size=8),
                        text_color=("gray50", "gray60")
                    )
                    conf_label.pack(pady=(0, 4))
        
        # Box identifier
        id_label = ctk.CTkLabel(
            container,
            text=f"Visual {idx + 1}",
            font=ctk.CTkFont(size=9, slant="italic"),
            text_color=("gray50", "gray60")
        )
        id_label.pack(pady=(0, 5))
        
        return container
    
    def _create_match_item(self, parent, match: Dict, item_number: int):
        """Create a compact match item display for the summary"""
        if match.get("content_type") != "matching_pair":
            return
        
        pair_data = match.get("pair_data", {})
        term = pair_data.get("term", "Unknown")
        matched = pair_data.get("match", "Unknown")
        confidence = match.get("confidence", 0) * 100
        
        # Create a compact horizontal layout
        match_frame = ctk.CTkFrame(
            parent,
            fg_color=("#E8F0FE", "#1C2333"),
            border_color=("#4A90E2", "#2A5298"),
            border_width=1,
            corner_radius=6
        )
        match_frame.pack(fill="x", pady=2)
        
        # Number badge
        num_label = ctk.CTkLabel(
            match_frame,
            text=f"{item_number}",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=("#4A90E2", "#2A5298"),
            corner_radius=4,
            width=25,
            height=25
        )
        num_label.pack(side="left", padx=(8, 5), pady=5)
        
        # Match text
        match_text = f"'{term}' ➡️ '{matched}'"
        match_label = ctk.CTkLabel(
            match_frame,
            text=match_text,
            font=ctk.CTkFont(size=10),
            anchor="w",
            wraplength=400
        )
        match_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Confidence badge
        if confidence > 0:
            conf_text = f"{confidence:.0f}%"
            conf_color = "#4CAF50" if confidence >= 90 else "#FF9800" if confidence >= 70 else "#F44336"
            conf_label = ctk.CTkLabel(
                match_frame,
                text=conf_text,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=conf_color
            )
            conf_label.pack(side="right", padx=(5, 8), pady=5)


class EnhancedAnswerPresenter:
    """Main class for presenting AI answers with enhanced visualizations"""
    
    def __init__(self, parent_scroll_frame: ctk.CTkScrollableFrame):
        self.parent_scroll_frame = parent_scroll_frame
        
    def detect_question_type(self, response_data: Dict) -> str:
        """
        Detect the question type from AI response
        
        Returns:
            Question type identifier
        """
        answers = response_data.get("answers", [])
        
        if not answers:
            return "unknown"
        
        # Check for matching pairs (drag-to-image type)
        matching_pairs = [a for a in answers if a.get("content_type") == "matching_pair"]
        if len(matching_pairs) >= 3:  # Multiple matches suggest drag-to-image
            return "drag_to_image"
        
        # Check for multiple choice
        mc_options = [a for a in answers if a.get("content_type") == "multiple_choice_option"]
        if len(mc_options) >= 2:
            return "multiple_choice"
        
        # Check for table completion
        if any(a.get("content_type") == "table_completion" for a in answers):
            return "table"
        
        # Check for sequence
        if any(a.get("content_type") == "ordered_sequence" for a in answers):
            return "sequence"
        
        # Default
        return "standard"
    
    def present_answers(self, response_data: Dict, image_path: Optional[str] = None):
        """
        Present answers using appropriate visualization based on question type
        
        Args:
            response_data: AI response data
            image_path: Path to the screenshot (optional, for visual questions)
        """
        question_type = self.detect_question_type(response_data)
        
        # Clear existing content
        for widget in self.parent_scroll_frame.winfo_children():
            widget.destroy()
        
        if question_type == "drag_to_image" and image_path:
            # Use special drag-to-image renderer
            renderer = DragToImageRenderer(self.parent_scroll_frame, image_path)
            matching_answers = [
                a for a in response_data.get("answers", [])
                if a.get("content_type") == "matching_pair"
            ]
            display = renderer.create_visual_matching_display(matching_answers)
            display.pack(fill="both", expand=True)
        else:
            # Standard display would be used (handled by main app)
            pass


def create_visual_answer_overlay(base_image_path: str, 
                                 matching_answers: List[Dict],
                                 output_path: str = "answer_overlay.png") -> str:
    """
    Create an annotated image showing the AI's matches visually
    
    Args:
        base_image_path: Path to original screenshot
        matching_answers: List of AI matching answers
        output_path: Where to save the annotated image
        
    Returns:
        Path to the created overlay image
    """
    try:
        img = Image.open(base_image_path)
        draw = ImageDraw.Draw(img)
        
        # Try to load a nice font
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 16)
                font_small = ImageFont.truetype("DejaVuSans.ttf", 12)
            except:
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # Draw arrows and labels for each match
        for idx, match in enumerate(matching_answers):
            pair_data = match.get("pair_data", {})
            term = pair_data.get("term", "")
            matched = pair_data.get("match", "")
            
            # This would draw arrows from text to images
            # Simplified for now - could calculate actual positions
            
        img.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error creating visual overlay: {e}")
        return base_image_path  # Return original if overlay fails