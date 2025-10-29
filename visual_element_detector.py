"""
Visual Element Detector - Identifies and extracts interactive regions from screenshots
Supports drag-to-image question types and other visual matching questions
"""

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from typing import List, Dict, Tuple, Optional
import json

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
        """
        Detect grid-based visual boxes using edge detection and contour analysis
        
        Args:
            min_box_size: Minimum size (width or height) for a valid box
            grid_rows: Expected number of rows (optional)
            grid_cols: Expected number of columns (optional)
            
        Returns:
            List of detected regions with coordinates and metadata
        """
        # Convert to numpy array for processing
        img_array = np.array(self.image.convert('L'))  # Grayscale
        
        # Apply edge detection (simple threshold-based for now)
        # This is a simplified version - could use OpenCV for better results
        edges = self._detect_edges_simple(img_array)
        
        # Find rectangular regions
        regions = self._find_rectangular_regions(edges, min_box_size)
        
        # If grid parameters provided, try to organize into grid
        if grid_rows and grid_cols:
            regions = self._organize_into_grid(regions, grid_rows, grid_cols)
        
        self.detected_regions = regions
        return regions
    
    def detect_standard_question_layout(self) -> Dict:
        """
        Detect common question layout patterns:
        - Top section with images/visual elements
        - Bottom section with draggable text options
        - Submit button at bottom
        
        Returns:
            Dictionary with detected layout regions
        """
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
        """
        Extract a sub-region from the image
        
        Args:
            x1, y1: Top-left coordinates
            x2, y2: Bottom-right coordinates
            output_path: Optional path to save the extracted region
            
        Returns:
            PIL Image of the extracted region
        """
        region = self.image.crop((x1, y1, x2, y2))
        
        if output_path:
            region.save(output_path)
            
        return region
    
    def extract_visual_boxes_from_grid(self, num_boxes: int = 6,
                                      grid_layout: str = "2x3",
                                      padding: int = 10) -> List[Dict]:
        """
        Extract individual visual boxes from a detected grid
        
        Args:
            num_boxes: Number of boxes expected
            grid_layout: Layout as "rows x cols" (e.g., "2x3" for 2 rows, 3 columns)
            padding: Padding to remove from each box edge
            
        Returns:
            List of extracted box info with image data
        """
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
                x1 = va_x1 + (col * box_width) + padding
                y1 = va_y1 + (row * box_height) + padding
                x2 = va_x1 + ((col + 1) * box_width) - padding
                y2 = va_y1 + ((row + 1) * box_height) - padding
                
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
        """
        Create an annotated version of the image showing detected boxes
        
        Args:
            boxes: List of detected boxes
            output_path: Path to save annotated image
            show_labels: Whether to show box labels
            
        Returns:
            Annotated PIL Image
        """
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
        # This is simplified - for production use OpenCV's Canny edge detector
        edges = np.zeros_like(img_array)
        edges[img_array > threshold] = 255
        return edges
    
    def _find_rectangular_regions(self, edges: np.ndarray, min_size: int) -> List[Dict]:
        """Find rectangular regions in edge image"""
        # Simplified region detection
        # In production, use OpenCV's findContours and boundingRect
        regions = []
        # Placeholder implementation
        return regions
    
    def _organize_into_grid(self, regions: List[Dict], rows: int, cols: int) -> List[Dict]:
        """Organize detected regions into a grid structure"""
        # Sort by position and assign to grid cells
        # Placeholder implementation
        return regions


def analyze_drag_to_image_question(image_path: str, 
                                   grid_layout: str = "2x3",
                                   num_boxes: int = 6) -> Dict:
    """
    Analyze a drag-to-image question and extract visual elements
    
    Args:
        image_path: Path to the screenshot
        grid_layout: Expected grid layout (e.g., "2x3")
        num_boxes: Number of visual boxes expected
        
    Returns:
        Dictionary with extracted information and box data
    """
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


if __name__ == "__main__":
    # Example usage
    test_image = "saved_screenshots/screenshot_20250913_030422.png"
    result = analyze_drag_to_image_question(test_image)
    print(f"Detected {len(result['boxes'])} boxes")
    print(f"Annotated image saved to: {result['annotated_image_path']}")