# Test Screenshots for Edmentum Item Types

This directory contains reference screenshots for testing all 15 Edmentum technology-enhanced item types.

## 📸 How to Add Test Screenshots

1. Navigate to an Edmentum question of the desired type
2. Take a full-screen screenshot showing the complete question
3. Save with the corresponding filename below
4. Place in this directory

## 📋 15 Edmentum Item Types

### Priority (Most Common):
- **05_hot_text.png** - Hot Text (Select text in passage) ⭐ CRITICAL
- **02_matched_pairs.png** - Matched Pairs (Drag-drop matching)
- **01_multiple_choice.png** - Multiple Choice (Standard radio buttons)
- **13_multiple_response.png** - Multiple Response (Select all that apply)

### Standard Types:
- **06_cloze_dropdown.png** - Cloze/Dropdown (Select from dropdown in sentence)
- **08_fill_blank.png** - Fill in the Blank (Type text answers)
- **11_multi_part.png** - Multi-Part (Question with Parts A, B, etc.)

### Advanced Types:
- **03_graphic_gap_match.png** - Graphic Gap Match (Drag items to image targets)
- **04_hot_spot.png** - Hot Spot (Click location on image)
- **07_graphing.png** - Graphing (Plot on coordinate grid)
- **09_sequence.png** - Sequence (Order items correctly)
- **10_graphic_tally.png** - Graphic Tally (Multiple valid arrangements)
- **12_number_line.png** - Number Line (Plot points on number line)
- **15_equation.png** - Equation (Enter math notation)

### Activity-Only:
- **14_freehand_drawing.png** - Freehand Drawing (Draw with tools, activities only)

## 🧪 Testing Instructions

1. Use "Load Screenshot" button in the app
2. Select a test screenshot from this directory
3. Click "Get AI Answer"
4. Verify the answer displays correctly with Edmentum styling
5. For hot text: Check green highlighting on selected passages
6. For matching pairs: Check term-definition alignment
7. For multiple choice: Check radio button styling and correct answer highlighting

## 📝 Notes

- Hot text questions MUST show green highlighted passages (not just text answers)
- Matching pairs should display in 2-column layout with visual connections
- All questions should use Edmentum color scheme (green for correct, blue accents)
- Report any rendering issues using the "Report Error" button

## ✅ Authentic Edmentum Screenshots Included

**This directory contains 2 authentic Edmentum screenshots** for testing the most critical question types!

These are real Edmentum questions captured from the platform, demonstrating actual question content and layout.

### Included Screenshots:

#### 05_hot_text.png - Hot Text (Select text in passage)
![Hot Text Question](05_hot_text.png)
**Question**: "Which excerpt from act I of Shakespeare's Twelfth Night informs the audience that Olivia has gone into a self-imposed seclusion?"
- Shows full passage with selectable text options in blue
- Demonstrates Edmentum's hot text selection interface
- Tests the app's ability to identify and highlight correct text excerpts

#### 06_cloze_dropdown.png - Cloze/Dropdown (Fill-in with dropdown)
![Cloze Dropdown Question](06_cloze_dropdown.png)
**Question**: "Sebastian describes his sister to Antonio in the excerpt below from Shakespeare's Twelfth Night. Complete the sentences with appropriate words from the drop-down menu."
- Shows passage with dropdown menus embedded in text
- Demonstrates Edmentum's cloze/dropdown interface
- Tests the app's ability to fill in dropdown selections correctly

### Using the Included Screenshots:
1. Launch the Homework Helper app: `python main.py`
2. Click "📁 Load Screenshot" button
3. Navigate to `test_screenshots/` directory
4. Select either `05_hot_text.png` or `06_cloze_dropdown.png`
5. Click "Get AI Answer" to test rendering

### Adding Your Own Screenshots (For Other 13 Types):
To test the remaining 13 Edmentum item types, capture your own screenshots:
1. Navigate to an Edmentum question of the desired type
2. Press `Win+Shift+S` (Windows) or `Cmd+Shift+4` (Mac)
3. Capture the full question area including all options/elements
4. Save with the corresponding filename from the list above (e.g., `01_multiple_choice.png`)
5. Place in this `test_screenshots` directory
6. Load in the app using "📁 Load Screenshot"

**Note**: Only 2 authentic screenshots are included in the repository due to copyright concerns. You must provide your own Edmentum screenshots for the other 13 question types.

---

Last Updated: 2025-10-30 | v1.0.24
