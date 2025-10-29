"""
Manual Coordinate Tool - Click-based coordinate measurement
Run this to manually identify box boundaries by clicking on the image
"""

from PIL import Image
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk


class ManualCoordinateTool:
    """Interactive tool for clicking and measuring coordinates"""
    
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size
        
        # Scale image if too large
        max_display = 900
        if self.width > max_display or self.height > max_display:
            scale = min(max_display / self.width, max_display / self.height)
            new_width = int(self.width * scale)
            new_height = int(self.height * scale)
            self.display_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.scale_factor = scale
        else:
            self.display_image = self.image
            self.scale_factor = 1.0
        
        self.points = []
        self.boxes = []
        
    def run(self):
        """Run the interactive coordinate tool"""
        root = tk.Tk()
        root.title("Manual Coordinate Tool - Click to Measure")
        
        # Instructions
        inst_frame = tk.Frame(root)
        inst_frame.pack(pady=10)
        
        tk.Label(inst_frame, text="INSTRUCTIONS:", font=("Arial", 12, "bold")).pack()
        tk.Label(inst_frame, text="1. Click TOP-LEFT corner of Box 1 (pie chart)").pack()
        tk.Label(inst_frame, text="2. Click BOTTOM-RIGHT corner of Box 1").pack()
        tk.Label(inst_frame, text="3. Repeat for each box (left-to-right, top-to-bottom)").pack()
        tk.Label(inst_frame, text="4. Press 'Done' when finished").pack()
        
        # Canvas for image
        canvas_frame = tk.Frame(root)
        canvas_frame.pack()
        
        self.canvas = Canvas(canvas_frame, width=self.display_image.width, height=self.display_image.height)
        self.canvas.pack()
        
        # Convert PIL to Tk image
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Status label
        self.status_label = tk.Label(root, text="Click TOP-LEFT of Box 1", font=("Arial", 11))
        self.status_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Clear Last", command=self.clear_last).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Done", command=lambda: self.finish(root)).pack(side=tk.LEFT, padx=5)
        
        root.mainloop()
        
    def on_click(self, event):
        """Handle mouse click"""
        # Convert display coordinates to original image coordinates
        orig_x = int(event.x / self.scale_factor)
        orig_y = int(event.y / self.scale_factor)
        
        self.points.append((orig_x, orig_y))
        
        # Draw point on canvas
        r = 3
        self.canvas.create_oval(event.x-r, event.y-r, event.x+r, event.y+r, fill="red", outline="black")
        self.canvas.create_text(event.x+10, event.y-10, text=f"{orig_x},{orig_y}", fill="red")
        
        # Update status
        point_num = len(self.points)
        if point_num % 2 == 1:
            box_num = (point_num // 2) + 1
            self.status_label.config(text=f"Click BOTTOM-RIGHT of Box {box_num}")
        elif point_num < 12:
            box_num = (point_num // 2) + 1
            self.status_label.config(text=f"Box {box_num-1} complete. Click TOP-LEFT of Box {box_num}")
            
            # Draw completed box
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]
            self.canvas.create_rectangle(
                int(x1 * self.scale_factor), int(y1 * self.scale_factor),
                int(x2 * self.scale_factor), int(y2 * self.scale_factor),
                outline="green", width=2
            )
            
            # Store box
            self.boxes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
        else:
            self.status_label.config(text="All 6 boxes measured! Click 'Done'")
    
    def clear_last(self):
        """Remove last clicked point"""
        if self.points:
            self.points.pop()
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            # Redraw all points
            for i, (x, y) in enumerate(self.points):
                display_x = int(x * self.scale_factor)
                display_y = int(y * self.scale_factor)
                r = 3
                self.canvas.create_oval(display_x-r, display_y-r, display_x+r, display_y+r, fill="red", outline="black")
                self.canvas.create_text(display_x+10, display_y-10, text=f"{x},{y}", fill="red")
    
    def finish(self, root):
        """Process measurements and close"""
        if len(self.boxes) < 6:
            self.status_label.config(text=f"Need 6 boxes, only have {len(self.boxes)}. Continue clicking.")
            return
        
        root.destroy()
        
        # Analyze measurements
        print("\n" + "="*70)
        print("MEASURED COORDINATES")
        print("="*70)
        
        for i, box in enumerate(self.boxes):
            w = box['x2'] - box['x1']
            h = box['y2'] - box['y1']
            print(f"Box {i+1}: ({box['x1']},{box['y1']}) to ({box['x2']},{box['y2']}) = {w}x{h}px")
        
        # Calculate average box size
        avg_w = sum(box['x2'] - box['x1'] for box in self.boxes) / len(self.boxes)
        avg_h = sum(box['y2'] - box['y1'] for box in self.boxes) / len(self.boxes)
        print(f"\nAverage Box Size: {avg_w:.0f}x{avg_h:.0f}px")
        
        # Calculate grid boundaries
        all_x1 = [box['x1'] for box in self.boxes]
        all_y1 = [box['y1'] for box in self.boxes]
        all_x2 = [box['x2'] for box in self.boxes]
        all_y2 = [box['y2'] for box in self.boxes]
        
        grid_x1, grid_y1 = min(all_x1), min(all_y1)
        grid_x2, grid_y2 = max(all_x2), max(all_y2)
        
        print(f"\nGrid Boundaries: ({grid_x1},{grid_y1}) to ({grid_x2},{grid_y2})")
        print(f"Grid Size: {grid_x2-grid_x1}x{grid_y2-grid_y1}px")
        
        # Calculate as percentages
        print(f"\nAs Percentages of Image ({self.width}x{self.height}):")
        print(f"  Grid Y Start: {grid_y1/self.height*100:.1f}% ({grid_y1}px)")
        print(f"  Grid Y End: {grid_y2/self.height*100:.1f}% ({grid_y2}px)")
        print(f"  Left Margin: {grid_x1/self.width*100:.1f}% ({grid_x1}px)")
        print(f"  Right Margin: {(self.width-grid_x2)/self.width*100:.1f}% ({self.width-grid_x2}px)")
        
        # Calculate spacing
        if len(self.boxes) >= 2:
            # Horizontal spacing (between Box 1 and Box 2)
            h_spacing = self.boxes[1]['x1'] - self.boxes[0]['x2']
            # Vertical spacing (between Box 1 and Box 4)
            if len(self.boxes) >= 4:
                v_spacing = self.boxes[3]['y1'] - self.boxes[0]['y2']
                print(f"\nSpacing: H={h_spacing}px, V={v_spacing}px")
        
        # Generate code
        print("\n" + "="*70)
        print("RECOMMENDED CODE FOR enhanced_answer_display.py")
        print("="*70)
        print(f"""
# Based on manual measurement:
visual_start_y = {grid_y1}  # or int(self.img_height * {grid_y1/self.height:.3f})
visual_end_y = {grid_y2}    # or int(self.img_height * {grid_y2/self.height:.3f})
left_margin = {grid_x1}     # or int(self.img_width * {grid_x1/self.width:.3f})
right_margin = {self.width - grid_x2}   # or int(self.img_width * {(self.width-grid_x2)/self.width:.3f})

# Average box size: {avg_w:.0f}x{avg_h:.0f}px
""")


if __name__ == "__main__":
    print("Manual Coordinate Measurement Tool")
    print("="*70)
    
    image_path = "../HW Helper Modern/saved_screenshots/screenshot_20250913_030422.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        exit(1)
    
    print(f"Loading: {image_path}")
    tool = ManualCoordinateTool(image_path)
    print(f"Image size: {tool.width}x{tool.height}")
    print("\nClick to measure box coordinates...")
    print("Follow the instructions in the window\n")
    
    tool.run()