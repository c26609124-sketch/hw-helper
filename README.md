# Homework Helper AI - Complete Documentation

**Latest Version**: v1.0.29 | **Auto-Update**: ✅ Enabled | **Error Reporting**: 🤖 Automatic

## 🎯 Overview
Homework Helper AI is an intelligent application that uses OpenRouter API to analyze homework questions from screenshots and provide detailed, formatted answers. It features advanced visual enhancements for drag-to-image questions, supports multiple question types, and includes an **automatic update system** that keeps your app current with the latest fixes and features.

## 🚀 Quick Start

**Launch the application:**
```bash
python main.py
```

**Note:** Run `main.py` (not `ui.py`) to ensure updates are checked before the UI loads. This prevents getting stuck on broken versions.

## ✨ Key Features

### Core Capabilities
- ✅ **Auto-Update System**: Automatically checks for and applies updates on startup
- ✅ **Browser Integration**: Launch and control Brave browser with remote debugging
- ✅ **Screenshot Capture**: Automated iframe detection and full-content capture
- ✅ **OpenRouter API**: Access to multiple vision-capable AI models
- ✅ **Visual Enhancement**: Intelligent rendering for drag-to-image questions
- ✅ **Multi-Format Support**: Multiple choice, matching, tables, sequences, and more
- ✅ **Image Cropping**: Interactive region selection with handles
- ✅ **Saved Screenshot Loading**: Test with previously captured questions
- ✅ **Progressive Streaming**: Real-time answer streaming with smooth animations
- ✅ **Response Validation**: Automatic detection and fixing of AI response errors

### Auto-Update System (NEW v1.0.0)
- 🔄 **Automatic Checks**: Checks for updates on every app startup
- ⬇️ **One-Click Updates**: Downloads and applies updates automatically
- 📋 **Changelog Display**: Shows what's new in each update
- ✅ **GitHub Integration**: Updates pulled directly from official repository
- 🔒 **Safe Updates**: Backup system protects your existing files

### Automatic Error Reporting (NEW v1.0.18)
- 🤖 **Instant Reporting**: Errors automatically sent to developer via Discord
- 📸 **Screenshot Included**: Current screenshot attached to error reports
- 📋 **Full Context**: System info, logs, and stack traces included
- ✅ **One-Click**: Just click "Report Error" button - no manual steps
- 🔒 **Privacy**: Only error data and screenshot sent, no personal info

### Visual Enhancement
- 📍 **Coordinate Detection**: Automatically identifies visual elements in drag-to-image questions
- 🖼️ **Box Extraction**: Extracts individual images from grid layouts (2×3, 3×2, etc.)
- 🎨 **Visual Matching Display**: Shows extracted images with AI-matched descriptions overlaid
- ✓ **Confidence Indicators**: Green borders, checkmarks, and percentage scores
- 📊 **Match Summary**: Compact list with arrows showing all detected matches

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd "HW Helper"
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Get your key from: https://openrouter.ai/keys
python ui.py
# Enter API key in Settings → Click "Save Settings"
```

### 3. Test with Saved Screenshot
```bash
# Click "📁 Load Screenshot"
# Select: screenshot_20250913_030422.png (drag-to-image example)
# Click "3. Get AI Answer"
# Expected: Visual grid with 6 boxes and matched descriptions
```

## 📁 File Structure

```
HW Helper/
├── ui.py                              # Main application
├── selenium_capture_logic.py          # Browser automation
├── enhanced_answer_display.py         # Visual rendering (NEW)
├── visual_element_detector.py         # Coordinate detection (NEW)
├── config.json                        # API configuration
├── requirements.txt                   # Python dependencies
├── chromedriver.exe                   # Selenium driver
│
├── README.md                          # This file
├── SETUP_GUIDE.md                     # Detailed setup instructions
├── MIGRATION_SUMMARY.md               # API migration details
├── TESTING_GUIDE.md                   # Testing procedures (NEW)
└── VISUAL_ENHANCEMENT_README.md       # Visual features docs (NEW)
```

## 🎓 Supported Question Types

### 1. Drag-to-Image Matching
**Visual**: Grid of images/charts with draggable text below

**Example**: "Drag each tile to the correct location on the image"

**Features**:
- Extracts 6 visual boxes from 2×3 grid
- Displays each box with matched text overlay
- Shows confidence scores and checkmarks
- Creates summary with numbered matches

**Screenshot**: `screenshot_20250913_030422.png`

### 2. Text Matching Pairs
**Visual**: Two columns of text to be matched

**Example**: "Match each civil rights activist to their organization"

**Display**: Clean text list with arrows (➡️)

**Screenshot**: `screenshot_20250913_034547.png`

### 3. Multiple Choice
**Visual**: Question with A, B, C, D options

**Example**: "Which of the following best identifies the irony?"

**Display**: All options listed, correct one highlighted green

**Screenshot**: `screenshot_20250918_020256.png`

### 4. Fill-in-the-Blank
**Visual**: Sentence with blank spaces or {{placeholders}}

**Display**: Question with answers integrated

### 5. Table Completion
**Visual**: Table with some cells to fill

**Display**: Full table with AI-provided cells in bold

### 6. Ordered Sequence
**Visual**: Items to arrange in order

**Display**: Numbered list in correct sequence

### 7. Mathematical Equations
**Visual**: Equation with slots to fill

**Display**: Special rendering with boxes and operators

## 🔧 Configuration

### Recommended Models
```json
{
  "api_key": "sk-or-v1-YOUR_KEY",
  "selected_model": "google/gemini-2.5-flash"
}
```

### Available Models
1. **google/gemini-2.5-flash** - Best balance (recommended)
2. **google/gemini-2.0-flash-exp:free** - Free tier
3. **moonshotai/kimi-vl-a3b-thinking:free** - Free alternative
4. **google/gemini-2.5-pro** - Highest accuracy

## 🎮 Usage Workflow

### Standard Workflow
```
Launch Brave → Navigate to Question → Capture → Get Answer
```

### Testing Workflow
```
Load Screenshot → (Optional: Crop) → Get Answer → Review
```

### With Visual Enhancement
```
Load Drag-to-Image Screenshot → Get Answer → See Visual Grid
```

## 📊 What's New in v2.0

### Major Updates
1. **Brave Browser Fix** - Removed deprecated `--disable-web-security` flag
2. **OpenRouter Migration** - Fully integrated OpenRouter API
3. **Visual Enhancement** - New drag-to-image rendering system
4. **Screenshot Loading** - Test with saved questions
5. **Enhanced Documentation** - 5 comprehensive guides

### Breaking Changes
- ❌ Gemini API direct calls removed (use OpenRouter)
- ✅ All existing features maintained
- ✅ Backward compatible configuration

## 🔍 Troubleshooting

### Browser Won't Launch
```
Error: --disable-web-security flag warning
Solution: ✅ FIXED in v2.0
```

### API Errors
```
Error: 401 Unauthorized
Solution: Check API key at https://openrouter.ai/keys

Error: 402 Payment Required
Solution: Add credits to OpenRouter account

Error: Timeout
Solution: Check internet connection, try different model
```

### Visual Enhancement Issues
```
Warning: Visual enhancement modules not available
Solution: Ensure enhanced_answer_display.py and visual_element_detector.py are present

Issue: Boxes don't align
Solution: Adjust coordinates in enhanced_answer_display.py (see VISUAL_ENHANCEMENT_README.md)
```

## 📚 Documentation Index

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **README.md** (this file) | Overview and quick reference | Start here |
| [**SETUP_GUIDE.md**](SETUP_GUIDE.md) | Installation and configuration | Setting up for first time |
| [**TESTING_GUIDE.md**](TESTING_GUIDE.md) | Testing procedures and benchmarks | Before production use |
| [**MIGRATION_SUMMARY.md**](MIGRATION_SUMMARY.md) | Technical changes and API migration | Understanding what changed |
| [**VISUAL_ENHANCEMENT_README.md**](VISUAL_ENHANCEMENT_README.md) | Drag-to-image feature details | Using visual features |

## 🧪 Testing

### Quick Test
```bash
python ui.py
# Load screenshot_20250913_030422.png
# Get AI Answer
# Verify: 6 boxes appear with matches
```

### Full Test Suite
See [`TESTING_GUIDE.md`](TESTING_GUIDE.md) for:
- Functionality tests
- API integration tests
- Visual enhancement tests
- Performance benchmarks
- Quality assurance checklists

## 💡 Tips & Best Practices

### For Best Results
1. **Use Recommended Model**: `google/gemini-2.5-flash` for balance
2. **Test First**: Load saved screenshots before live capture
3. **Verify Confidence**: >90% = high confidence, <70% = review needed
4. **Check Activity Log**: Detailed debug information available
5. **Save API Costs**: Use free models for testing

### For Drag-to-Image Questions
1. Ensure full grid is visible in screenshot
2. Avoid cropping the visual boxes area
3. Include all draggable text options in capture
4. Review coordinate alignment if boxes misalign

### For Live Capture
1. Launch Brave first with "🚀 Launch Brave Browser"
2. Navigate to question and wait for full page load
3. Click "1. Capture Question"
4. Verify screenshot before requesting AI answer

## 🛠️ Advanced Customization

### Custom Brave Path
Edit [`ui.py:400`](ui.py:400):
```python
brave_exe_path = r"YOUR\PATH\TO\brave.exe"
```

### Custom Grid Coordinates
Edit [`enhanced_answer_display.py:128-132`](enhanced_answer_display.py:128-132):
```python
visual_start_y = int(self.img_height * 0.12)  # Adjust for your platform
visual_end_y = int(self.img_height * 0.58)
left_margin = int(self.img_width * 0.20)
```

### Custom Selenium Selectors
Edit [`selenium_capture_logic.py:23-31`](selenium_capture_logic.py:23-31):
```python
MAIN_CONTAINER_LOCATOR_VALUE = "your-class-name"
IFRAME_ID = "your-iframe-id"
```

## 📈 Performance

### Processing Times
- Browser launch: 2-3 seconds
- Screenshot capture: 3-5 seconds
- API response: 10-30 seconds (varies by model)
- Visual rendering: <1 second

### Resource Usage
- Memory: ~50-100MB (normal operation)
- Disk: ~5-15MB per screenshot
- Network: ~1-5MB per API call (includes image upload)

## 🔒 Security

### Best Practices
1. ✅ Never commit API keys to version control
2. ✅ Use environment variables for sensitive data
3. ✅ Rotate API keys regularly
4. ✅ Monitor usage for anomalies
5. ✅ Keep dependencies updated

### Data Privacy
- Screenshots saved locally only
- API calls encrypted (HTTPS)
- No data retention by default
- Temporary files cleaned up automatically

## 🌟 Example Use Cases

### Use Case 1: Statistics Homework
**Question Type**: Drag-to-image with charts and graphs

**Workflow**:
1. Capture screenshot showing statistical charts
2. AI identifies each chart type
3. Matches descriptions to correct charts
4. Displays visual grid with confidence scores

**Result**: Visual grid showing 6 charts with matched statistical concepts

### Use Case 2: History Matching
**Question Type**: Text-to-text matching

**Workflow**:
1. Capture civil rights activists question
2. AI matches each person to their organization
3. Displays clean list format

**Result**: 4 matches with 98% confidence each

### Use Case 3: Literature Analysis
**Question Type**: Multiple choice with long passages

**Workflow**:
1. Capture passage and question
2. AI analyzes all options
3. Highlights correct answer with explanation

**Result**: All options listed, correct one marked ✅ with reasoning

## 📞 Support & Resources

### Documentation
- 📖 [Setup Guide](SETUP_GUIDE.md) - Getting started
- 🧪 [Testing Guide](TESTING_GUIDE.md) - Quality assurance
- 🎨 [Visual Enhancement](VISUAL_ENHANCEMENT_README.md) - Advanced features
- 📝 [Migration Summary](MIGRATION_SUMMARY.md) - What changed in v2.0

### External Resources
- **OpenRouter Dashboard**: https://openrouter.ai/account
- **API Documentation**: https://openrouter.ai/docs
- **Model Pricing**: https://openrouter.ai/models
- **Usage Tracking**: https://openrouter.ai/activity

## 🐛 Known Issues

### Minor Issues
1. **Grid Alignment**: May need coordinate adjustment for different platforms
2. **Long Text Wrapping**: Very long options may overflow in some cases
3. **Memory Usage**: Large images (>10MB) may slow down processing

### Workarounds Provided
- Coordinate customization guide in VISUAL_ENHANCEMENT_README.md
- Text wrapping handled by CTkLabel wraplength parameter
- Image resizing applied automatically

## 🎯 Roadmap

### v2.1 (Planned)
- [ ] OpenCV-based automatic coordinate detection
- [ ] Support for 3×3 and other grid layouts
- [ ] Interactive coordinate adjustment UI
- [ ] Multiple platform presets (Edmentum, Canvas, etc.)
- [ ] Export answers to clipboard/file

### v2.2 (Future)
- [ ] Streaming API responses with progress indicator
- [ ] Batch processing for multiple questions
- [ ] Answer caching to reduce API calls
- [ ] Chrome/Edge browser support
- [ ] Mobile-friendly interface

### v3.0 (Vision)
- [ ] Machine learning for improved matching
- [ ] OCR for text extraction from images
- [ ] Voice input for questions
- [ ] Multi-language support
- [ ] Cloud sync for saved screenshots

## 📄 License
This project is for educational purposes. Please ensure compliance with your educational institution's academic integrity policies.

## ⚠️ Disclaimer
This tool is designed to help understand homework, not to facilitate cheating. Always verify AI-generated answers and use the tool responsibly and ethically.

## 🏆 Credits
- **OpenRouter API**: https://openrouter.ai
- **CustomTkinter**: Modern UI framework
- **Selenium**: Browser automation
- **PIL**: Image processing
- **Google Gemini Models**: Via OpenRouter

## 📜 Version History

### v2.0.0 (Current) - Major Update
- ✅ Fixed Brave browser launch error
- ✅ Migrated to OpenRouter API
- ✅ Added visual enhancement for drag-to-image questions
- ✅ Implemented screenshot loading
- ✅ Created comprehensive documentation suite
- ✅ Improved error handling and logging

### v1.0.0 - Initial Release
- Basic screenshot capture
- Gemini API integration
- Multiple question type support

---

## 🚦 Getting Started

1. **Read**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. **Configure**: Set your OpenRouter API key
3. **Test**: Load a saved screenshot
4. **Use**: Capture live homework questions
5. **Review**: Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for quality assurance

---

**Need Help?**
- 📖 Start with [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 🔧 Having issues? See [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)
- 🎨 Want visual features? Read [VISUAL_ENHANCEMENT_README.md](VISUAL_ENHANCEMENT_README.md)
- 🧪 Ready to test? Follow [TESTING_GUIDE.md](TESTING_GUIDE.md)

**Ready to use?** Run `python ui.py` and click "📁 Load Screenshot" to test with the 4 saved examples!