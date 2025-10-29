"""
Coordinate Calibrator - Interactive tool to fine-tune visual box extraction
Run this to visually test and adjust cropping coordinates
"""

from PIL import Image, ImageDraw, ImageFont
import os

class CoordinateCalibrator:
    """Interactive calibrator for fine-tuning box extraction coordinates"""
    
    def __init__(self, image_path: str):
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size
        print(f"Image loaded: {self.width}x{self.height}")
        
    def test_coordinates(self, 
                        visual_start_pct: float = 0.16,
                        visual_end_pct: float = 0.48,
                        left_margin_pct: float = 0.185,
                        right_margin_pct: float = 0.185,
                        h_padding: int = 22,
                        v_padding: int = 20,
                        extra_bottom: int = 8,
                        rows: int = 2,
                        cols: int = 3):
        """
        Test a set of coordinates and generate annotated image
        
        Args:
            visual_start_pct: Percentage where grid starts (0.0-1.0)
            visual_end_pct: Percentage where grid ends (0.0-1.0)
            left_margin_pct: Left margin percentage
            right_margin_pct: Right margin percentage
            h_padding: Horizontal padding in pixels
            v_padding: Vertical padding in pixels
            extra_bottom: Extra pixels to crop from bottom
            rows: Number of grid rows
            cols: Number of grid columns
        """
        visual_start_y = int(self.height * visual_start_pct)
        visual_end_y = int(self.height * visual_end_pct)
        visual_height = visual_end_y - visual_start_y
        
        left_margin = int(self.width * left_margin_pct)
        right_margin = int(self.width * right_margin_pct)
        visual_width = self.width - left_margin - right_margin
        
        box_width = visual_width // cols
        box_height = visual_height // rows
        
        # Create annotated image
        annotated = self.image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        boxes = []
        for row in range(rows):
            for col in range(cols):
                # Calculate box with padding
                x1 = left_margin + (col * box_width) + h_padding
                y1 = visual_start_y + (row * box_height) + v_padding
                x2 = left_margin + ((col + 1) * box_width) - h_padding
                y2 = visual_start_y + ((row + 1) * box_height) - v_padding - extra_bottom
                
                # Draw rectangle
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                
                # Draw label
                label = f"Box {row*cols + col + 1}"
                draw.text((x1 + 5, y1 + 5), label, fill="red", font=font)
                
                # Draw dimensions
                w, h = x2 - x1, y2 - y1
                dim_text = f"{w}x{h}"
                draw.text((x1 + 5, y2 - 20), dim_text, fill="blue", font=font)
                
                boxes.append({
                    "index": row*cols + col,
                    "row": row,
                    "col": col,
                    "coords": (x1, y1, x2, y2),
                    "size": (w, h)
                })
        
        # Draw grid boundaries
        draw.rectangle([left_margin, visual_start_y, self.width - right_margin, visual_end_y], 
                      outline="green", width=2)
        
        # Save annotated image
        output_path = "calibration_test.png"
        annotated.save(output_path)
        print(f"\n[OK] Annotated image saved: {output_path}")
        print(f"\n[OK] Grid Analysis:")
        print(f"  Visual Area: Y {visual_start_y}-{visual_end_y} (height: {visual_height}px)")
        print(f"  Content Width: {visual_width}px (margins: L{left_margin}, R{right_margin})")
        print(f"  Box Dimensions: {box_width}x{box_height} per cell")
        print(f"  Padding: H={h_padding}px, V={v_padding}px, BottomExtra={extra_bottom}px")
        
        print(f"\n[OK] Individual Boxes:")
        for box in boxes:
            print(f"  Box {box['index']+1} [{box['row']},{box['col']}]: "
                  f"({box['coords'][0]},{box['coords'][1]}) to ({box['coords'][2]},{box['coords'][3]}) "
                  f"= {box['size'][0]}x{box['size'][1]}px")
        
        # Extract and save individual boxes
        for box in boxes:
            x1, y1, x2, y2 = box['coords']
            box_img = self.image.crop((x1, y1, x2, y2))
            box_path = f"box_{box['index']+1}_extracted.png"
            box_img.save(box_path)
        
        print(f"\n[OK] Extracted {len(boxes)} individual box images")
        print(f"   Check: box_1_extracted.png through box_6_extracted.png")
        
        return boxes, output_path


def run_calibration(image_path: str = None):
    """Run interactive calibration session"""
    
    if not image_path:
        # Use default test image
        image_path = "../HW Helper Modern/saved_screenshots/screenshot_20250913_030422.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print("=" * 70)
    print("COORDINATE CALIBRATOR - Visual Box Extraction Fine-Tuning")
    print("=" * 70)
    
    calibrator = CoordinateCalibrator(image_path)
    
    # Test HARDCODED coordinates approach
    print("\n[*] Testing HARDCODED coordinates for pixel-perfect accuracy...")
    
    # For this specific screenshot, use absolute pixel coordinates
    # These are measured from the actual visual elements
    hardcoded_test_boxes = [
        # FINAL REFINED coordinates - eliminates visible cell borders
        # Row 1 (Top row of visuals)
        (250, 180, 356, 276),  # Box 1: Pie chart (106x96px)
        (400, 180, 506, 276),  # Box 2: China map (106x96px)
        (550, 180, 653, 276),  # Box 3: Empire State Building (103x96px) - tighter right
        # Row 2 (Bottom row of visuals)
        (250, 340, 356, 436),  # Box 4: Text comparison (106x96px)
        (400, 340, 506, 436),  # Box 5: Football diagram (106x96px)
        (550, 340, 653, 436),  # Box 6: Venn/circles (103x96px) - tighter right
    ]
    
    # Create annotated image with hardcoded boxes
    annotated = calibrator.image.copy()
    draw = ImageDraw.Draw(annotated)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    boxes = []
    for idx, (x1, y1, x2, y2) in enumerate(hardcoded_test_boxes):
        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        
        # Label
        draw.text((x1 + 5, y1 + 5), f"Box {idx+1}", fill="red", font=font)
        
        # Dimensions
        w, h = x2 - x1, y2 - y1
        draw.text((x1 + 5, y2 - 20), f"{w}x{h}", fill="blue", font=font)
        
        # Extract and save individual box
        box_img = calibrator.image.crop((x1, y1, x2, y2))
        box_img.save(f"box_{idx+1}_extracted.png")
        
        boxes.append({
            "index": idx,
            "coords": (x1, y1, x2, y2),
            "size": (w, h)
        })
    
    annotated_path = "calibration_test.png"
    annotated.save(annotated_path)
    
    print(f"\n[OK] Annotated image saved: {annotated_path}")
    print(f"\n[OK] Grid Analysis (HARDCODED):")
    print(f"  Using absolute pixel coordinates for maximum accuracy")
    print(f"\n[OK] Individual Boxes:")
    for box in boxes:
        print(f"  Box {box['index']+1}: "
              f"({box['coords'][0]},{box['coords'][1]}) to ({box['coords'][2]},{box['coords'][3]}) "
              f"= {box['size'][0]}x{box['size'][1]}px")
    
    print(f"\n[OK] Extracted 6 individual box images")
    
    annotated_path = annotated_path
    
    print("\n" + "=" * 70)
    print("[>] NEXT STEPS:")
    print("=" * 70)
    print("1. Open calibration_test.png to see RED boxes overlaid on image")
    print("2. Open box_1_extracted.png through box_6_extracted.png")
    print("3. Check if boxes capture ONLY the visual elements (no labels/text)")
    print("4. If adjustment needed, modify values in enhanced_answer_display.py")
    print("\n[!] TIPS:")
    print("   - RED boxes show extraction area")
    print("   - GREEN box shows overall grid area")
    print("   - Boxes should exclude text labels like 'Your Money', 'Thoreau'")
    print("   - Boxes should exclude small labels like 'X', 'O', 'Lewis'")
    print("   - Boxes should be TIGHT around just the visual element")
    
    print("\n[+] To adjust coordinates, edit enhanced_answer_display.py:")
    print("   visual_start_pct - Move grid up/down (higher = lower on screen)")
    print("   visual_end_pct - Grid height (lower = shorter grid)")
    print("   left_margin_pct - Move grid left/right")
    print("   h_padding - Horizontal crop tightness")
    print("   v_padding - Vertical crop tightness")
    print("   extra_bottom - Remove labels at bottom of boxes")
    
    return boxes, annotated_path


if __name__ == "__main__":
    print("\n[>>] Starting Coordinate Calibration...")
    result = run_calibration()
    
    if result:
        print("\n[OK] Calibration complete! Check the output files.")
        print("\n[FILES] Generated Files:")
        print("   - calibration_test.png (annotated with red boxes)")
        print("   - box_1_extracted.png to box_6_extracted.png (individual crops)")
    
    print("\n" + "=" * 70)
    input("\nPress Enter to exit...")