"""
Edmentum Visual Components
==========================
CustomTkinter components that replicate Edmentum's exact visual style
for displaying questions and answers.

Based on official Edmentum Technology-Enhanced Item Types:
https://cdn.edmentum.com/assets/media/
"""

import customtkinter as ctk
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageTk
import re


# ============================================================================
# EDMENTUM STYLE CONSTANTS
# ============================================================================

EDMENTUM_STYLES = {
    # Colors - Light Mode
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F8F9FA',
    'bg_container': '#FAFBFC',
    'bg_info': '#E7F3FF',  # Light blue for info boxes

    # Blue (Primary)
    'blue_primary': '#0066CC',
    'blue_light': '#E7F3FF',
    'blue_hover': '#D4E9FF',
    'blue_selected': '#CCE5FF',
    'blue_border': '#99CCFF',  # Medium blue for borders

    # Green (Correct)
    'green_correct': '#28A745',
    'green_light': '#D4EDDA',
    'green_border': '#C3E6CB',

    # Gray
    'gray_border': '#DEE2E6',
    'gray_light': '#E9ECEF',
    'gray_text': '#6C757D',
    'gray_dark': '#495057',

    # Orange (Confidence)
    'orange_medium': '#FFA500',
    'orange_light': '#FFF3CD',

    # Red (Incorrect - for reference)
    'red_incorrect': '#DC3545',
    'red_light': '#F8D7DA',

    # Typography
    'font_family': 'Arial',
    'font_size_question': 15,
    'font_size_option': 14,
    'font_size_label': 13,
    'font_weight_question': 'normal',
    'font_weight_option': 'normal',

    # Spacing
    'padding_container': 20,
    'padding_question': 16,
    'padding_option': 12,
    'margin_option': 8,
    'border_radius': 6,
    'border_width': 1,
}

# Dark mode adaptations
EDMENTUM_DARK_STYLES = {
    'bg_primary': '#1E1E1E',
    'bg_secondary': '#2D2D2D',
    'bg_container': '#252525',
    'bg_info': '#1a2332',  # Dark blue for info boxes
    'blue_border': '#4d79cc',  # Brighter blue for dark mode borders
    'gray_border': '#404040',
    'gray_light': '#353535',
    'gray_text': '#B0B0B0',
    'gray_dark': '#E0E0E0',
    # Green colors for dark mode (darker green with good contrast)
    'green_correct': '#4CAF50',  # Brighter green for dark mode
    'green_light': '#1a311a',     # Dark green background
    'green_border': '#4CAF50',
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_style(key: str, appearance_mode: str = None) -> str:
    """Get a style value, accounting for light/dark mode"""
    if appearance_mode is None:
        appearance_mode = ctk.get_appearance_mode()

    if appearance_mode == "Dark" and key in EDMENTUM_DARK_STYLES:
        return EDMENTUM_DARK_STYLES[key]
    return EDMENTUM_STYLES.get(key, '')


def create_circle_badge(parent, letter: str, is_correct: bool = False,
                        size: int = 32) -> ctk.CTkFrame:
    """
    Create a circular badge with a letter (A/B/C/D)

    Args:
        parent: Parent widget
        letter: Single letter to display
        is_correct: If True, use green styling
        size: Diameter of circle in pixels

    Returns:
        CTkFrame containing the badge
    """
    color = EDMENTUM_STYLES['green_correct'] if is_correct else EDMENTUM_STYLES['blue_primary']

    badge = ctk.CTkFrame(
        parent,
        width=size,
        height=size,
        corner_radius=size // 2,
        fg_color=color,
        border_width=0
    )
    badge.pack_propagate(False)

    label = ctk.CTkLabel(
        badge,
        text=letter,
        font=("Arial", 14, "bold"),
        text_color="white"
    )
    label.place(relx=0.5, rely=0.5, anchor="center")

    return badge


# ============================================================================
# BASE COMPONENT CLASS
# ============================================================================

class EdmentumComponent:
    """Base class for all Edmentum components"""

    def __init__(self, parent):
        self.parent = parent
        self.appearance_mode = ctk.get_appearance_mode()

    def get_color(self, key: str) -> str:
        """Get color based on current appearance mode"""
        return get_style(key, self.appearance_mode)


# ============================================================================
# QUESTION CONTAINER
# ============================================================================

class EdmentumQuestionContainer(EdmentumComponent):
    """
    Main wrapper for Edmentum-style questions
    Provides consistent border, padding, and question number display
    """

    def __init__(self, parent, question_number: Optional[int] = None):
        super().__init__(parent)

        # Main container
        self.container = ctk.CTkFrame(
            parent,
            fg_color=self.get_color('bg_primary'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=EDMENTUM_STYLES['border_width'],
            border_color=self.get_color('gray_border')
        )
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # Question number badge (optional)
        if question_number:
            number_frame = ctk.CTkFrame(
                self.container,
                fg_color=self.get_color('blue_light'),
                corner_radius=4
            )
            number_frame.pack(anchor="nw", padx=15, pady=15)

            number_label = ctk.CTkLabel(
                number_frame,
                text=f"Question {question_number}",
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
                text_color=EDMENTUM_STYLES['blue_primary'],
                padx=10,
                pady=4
            )
            number_label.pack()

        # Content area where question and answers will be added
        self.content_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=EDMENTUM_STYLES['padding_container'])

    def get_content_frame(self) -> ctk.CTkFrame:
        """Returns the frame where question content should be added"""
        return self.content_frame


# ============================================================================
# MULTIPLE CHOICE COMPONENT
# ============================================================================

class EdmentumMultipleChoice(EdmentumComponent):
    """
    Multiple choice question with A/B/C/D radio button options
    Matches Edmentum's Multiple Choice visual style
    """

    def __init__(self, parent, question_text: str, options: List[Dict],
                 correct_answer_id: str = None):
        """
        Args:
            parent: Parent widget
            question_text: The question text to display
            options: List of dicts with 'label', 'text', 'id', 'is_correct'
            correct_answer_id: ID of the correct answer (for highlighting)
        """
        super().__init__(parent)
        self.question_text = question_text
        self.options = options
        self.correct_answer_id = correct_answer_id

        self._build_ui()

    def _build_ui(self):
        """Build the multiple choice interface"""
        # Question text
        question_label = ctk.CTkLabel(
            self.parent,
            text=self.question_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
            text_color=self.get_color('gray_dark'),
            wraplength=700,
            justify="left",
            anchor="w"
        )
        question_label.pack(fill="x", pady=(0, 20))

        # Options container
        options_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)

        # Render each option
        for option in self.options:
            self._create_option(options_frame, option)

    def _create_option(self, parent, option: Dict):
        """Create a single multiple choice option"""
        is_correct = option.get('is_correct', False) or option.get('id') == self.correct_answer_id

        # Option container (hoverable)
        option_frame = ctk.CTkFrame(
            parent,
            fg_color=self.get_color('green_light') if is_correct else self.get_color('bg_secondary'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=2 if is_correct else 1,
            border_color=EDMENTUM_STYLES['green_correct'] if is_correct else self.get_color('gray_border'),
            height=50
        )
        option_frame.pack(fill="x", pady=EDMENTUM_STYLES['margin_option'])

        # Inner horizontal layout
        inner_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=12, pady=10)

        # Letter badge (A/B/C/D)
        letter = option.get('label', '?')
        badge = create_circle_badge(inner_frame, letter, is_correct=is_correct)
        badge.pack(side="left", padx=(0, 12))

        # Option text with contrasting color
        text_content = option.get('text', option.get('text_content', ''))
        # Use dark text for correct answers in light mode, light text in dark mode
        text_color = "#155724" if (is_correct and self.appearance_mode == "Light") else self.get_color('gray_dark')
        option_label = ctk.CTkLabel(
            inner_frame,
            text=text_content,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option']),
            text_color=text_color,
            wraplength=600,
            justify="left",
            anchor="w"
        )
        option_label.pack(side="left", fill="x", expand=True)

        # Checkmark for correct answer
        if is_correct:
            checkmark = ctk.CTkLabel(
                inner_frame,
                text="✓",
                font=("Arial", 18, "bold"),
                text_color=EDMENTUM_STYLES['green_correct']
            )
            checkmark.pack(side="right", padx=(10, 0))

        # NOTE: Confidence badges removed for multiple choice
        # The is_correct_option field is the authoritative indicator of correctness
        # Confidence can be misleading when AI marks all options with similar high confidence


# ============================================================================
# MATCHED PAIRS COMPONENT
# ============================================================================

class EdmentumMatchedPairs(EdmentumComponent):
    """
    Matched pairs / drag-and-drop question
    Three-column layout: left items | center boxes | right items (matched)
    """

    def __init__(self, parent, question_text: str, pairs: List[Dict]):
        """
        Args:
            parent: Parent widget
            question_text: The question text
            pairs: List of dicts with 'term', 'match', 'pair_number', 'confidence'
        """
        super().__init__(parent)
        self.question_text = question_text
        self.pairs = pairs

        self._build_ui()

    def _build_ui(self):
        """Build the matched pairs interface"""
        # Question text
        question_label = ctk.CTkLabel(
            self.parent,
            text=self.question_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
            text_color=self.get_color('gray_dark'),
            wraplength=700,
            justify="left",
            anchor="w"
        )
        question_label.pack(fill="x", pady=(0, 20))

        # Main pairs container
        pairs_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        pairs_container.pack(fill="both", expand=True, pady=10)

        # Headers
        header_frame = ctk.CTkFrame(pairs_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        left_header = ctk.CTkLabel(
            header_frame,
            text="Terms",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=self.get_color('gray_text'),
            width=250
        )
        left_header.pack(side="left", padx=2)

        center_spacer = ctk.CTkFrame(header_frame, fg_color="transparent", width=40)
        center_spacer.pack(side="left")

        right_header = ctk.CTkLabel(
            header_frame,
            text="Matches",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=self.get_color('gray_text'),
            width=250
        )
        right_header.pack(side="left", padx=2)

        # Render each pair
        for i, pair in enumerate(self.pairs):
            self._create_pair_row(pairs_container, pair, i + 1)

    def _create_pair_row(self, parent, pair: Dict, pair_number: int):
        """Create a single pair row"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=6)

        # Left: Term
        term_text = pair.get('term', pair.get('text_content', ''))
        term_frame = ctk.CTkFrame(
            row_frame,
            fg_color=self.get_color('bg_secondary'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=1,
            border_color=self.get_color('gray_border'),
            width=250,
            height=60
        )
        term_frame.pack(side="left", padx=5)
        term_frame.pack_propagate(False)

        term_label = ctk.CTkLabel(
            term_frame,
            text=term_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option']),
            text_color=self.get_color('gray_dark'),
            wraplength=230,
            justify="left"
        )
        term_label.pack(expand=True, padx=10, pady=10)

        # Center: Arrow/Box
        center_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=80)
        center_frame.pack(side="left")

        arrow_label = ctk.CTkLabel(
            center_frame,
            text="➡️",
            font=("Arial", 20)
        )
        arrow_label.pack(expand=True)

        # Right: Match
        match_data = pair.get('pair_data', {}) if 'pair_data' in pair else pair
        match_text = match_data.get('match', match_data.get('match_value', ''))

        match_frame = ctk.CTkFrame(
            row_frame,
            fg_color=self.get_color('blue_light'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=2,
            border_color=EDMENTUM_STYLES['blue_primary'],
            width=250,
            height=60
        )
        match_frame.pack(side="left", padx=5)
        match_frame.pack_propagate(False)

        match_inner = ctk.CTkFrame(match_frame, fg_color="transparent")
        match_inner.pack(fill="both", expand=True, padx=10, pady=10)

        match_label = ctk.CTkLabel(
            match_inner,
            text=match_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option']),
            text_color=EDMENTUM_STYLES['blue_primary'],
            wraplength=210,
            justify="left"
        )
        match_label.pack(side="left", expand=True)

        # Checkmark
        checkmark = ctk.CTkLabel(
            match_inner,
            text="✓",
            font=("Arial", 16, "bold"),
            text_color=EDMENTUM_STYLES['green_correct']
        )
        checkmark.pack(side="right")

        # Confidence (optional)
        confidence = pair.get('confidence')
        if confidence:
            conf_label = ctk.CTkLabel(
                row_frame,
                text=f"{int(confidence * 100)}%",
                font=(EDMENTUM_STYLES['font_family'], 11),
                text_color=self.get_color('gray_text')
            )
            conf_label.pack(side="left", padx=10)


# ============================================================================
# DROPDOWN COMPONENT
# ============================================================================

class EdmentumDropdown(EdmentumComponent):
    """
    Dropdown/cloze question with inline dropdown selections
    """

    def __init__(self, parent, question_text: str, dropdowns: List[Dict]):
        """
        Args:
            parent: Parent widget
            question_text: Question text with {{placeholder}} markers
            dropdowns: List of dicts with 'dropdown_id', 'selected_text', 'confidence'
        """
        super().__init__(parent)
        self.question_text = question_text
        self.dropdowns = dropdowns

        self._build_ui()

    def _build_ui(self):
        """Build the dropdown question interface"""
        # Parse question text and insert dropdown widgets
        text = self.question_text

        # Create a frame to hold mixed text and dropdown widgets
        content_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        content_frame.pack(fill="x", pady=10)

        # Find all placeholders
        placeholder_pattern = r'\{\{([^}]+)\}\}'
        matches = list(re.finditer(placeholder_pattern, text))

        if not matches:
            # No placeholders, just display text
            label = ctk.CTkLabel(
                content_frame,
                text=text,
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
                text_color=self.get_color('gray_dark'),
                wraplength=700,
                justify="left",
                anchor="w"
            )
            label.pack(fill="x")
            return

        # Build text with inline dropdowns - use CTkTextbox for thread-safe rendering
        current_pos = 0

        # Use CTkTextbox instead of raw Tkinter Text widget (thread-safe)
        text_display = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
            fg_color=self.get_color('bg_primary'),
            text_color=self.get_color('gray_dark'),
            border_width=0,
            height=100,
            activate_scrollbars=False
        )
        text_display.pack(fill="x", pady=5)

        # Build the full text with dropdowns shown as [selected_value]
        full_text = ""
        for match in matches:
            # Text before placeholder
            before_text = text[current_pos:match.start()]
            full_text += before_text

            # Dropdown placeholder (show selected value inline)
            placeholder_id = match.group(1)
            dropdown_data = self._find_dropdown(placeholder_id)
            if dropdown_data:
                selected_text = dropdown_data.get('selected_text',
                                                 dropdown_data.get('text_content', '???'))
                # Add dropdown selection with visual indicator
                full_text += f" [{selected_text}] "

            current_pos = match.end()

        # Text after last placeholder
        after_text = text[current_pos:]
        full_text += after_text

        # Insert the complete text
        text_display.insert("1.0", full_text)

        # Make read-only
        text_display.configure(state="disabled")

    def _find_dropdown(self, placeholder_id: str) -> Optional[Dict]:
        """Find dropdown data by placeholder ID"""
        for dd in self.dropdowns:
            dd_id = dd.get('dropdown_id', dd.get('answer_id', ''))
            if placeholder_id in dd_id or dd_id in placeholder_id:
                return dd
        return None

    def _add_text_segment(self, parent, text: str):
        """Add a text segment with proper text wrapping"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
            text_color=self.get_color('gray_dark'),
            wraplength=650,
            justify="left",
            anchor="w"
        )
        label.pack(side="left", padx=2)

    def _add_dropdown_widget(self, parent, dropdown_data: Dict):
        """Add an inline dropdown widget showing the selected value"""
        selected_text = dropdown_data.get('selected_text',
                                          dropdown_data.get('text_content', '???'))

        # Dropdown-style frame
        dd_frame = ctk.CTkFrame(
            parent,
            fg_color=self.get_color('blue_light'),
            corner_radius=4,
            border_width=2,
            border_color=EDMENTUM_STYLES['blue_primary'],
            height=32
        )
        dd_frame.pack(side="left", padx=4)

        # Inner content
        inner = ctk.CTkFrame(dd_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=8, pady=4)

        value_label = ctk.CTkLabel(
            inner,
            text=selected_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option']),
            text_color=EDMENTUM_STYLES['blue_primary']
        )
        value_label.pack(side="left")

        # Dropdown arrow
        arrow = ctk.CTkLabel(
            inner,
            text="▼",
            font=("Arial", 8),
            text_color=EDMENTUM_STYLES['blue_primary']
        )
        arrow.pack(side="left", padx=(6, 0))


# ============================================================================
# FILL IN THE BLANK COMPONENT
# ============================================================================

class EdmentumFillBlank(EdmentumComponent):
    """
    Fill in the blank question with text input boxes
    """

    def __init__(self, parent, question_text: str, blanks: List[Dict]):
        """
        Args:
            parent: Parent widget
            question_text: Question text with {{placeholder}} markers
            blanks: List of dicts with 'answer_id', 'text_content', 'confidence'
        """
        super().__init__(parent)
        self.question_text = question_text
        self.blanks = blanks

        self._build_ui()

    def _build_ui(self):
        """Build the fill-in-the-blank interface"""
        text = self.question_text

        content_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        content_frame.pack(fill="x", pady=10)

        # Find all placeholders
        placeholder_pattern = r'\{\{([^}]+)\}\}'
        matches = list(re.finditer(placeholder_pattern, text))

        if not matches:
            # No placeholders, just display text
            label = ctk.CTkLabel(
                content_frame,
                text=text,
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
                text_color=self.get_color('gray_dark'),
                wraplength=700,
                justify="left",
                anchor="w"
            )
            label.pack(fill="x")
            return

        # Build text with inline input boxes
        current_pos = 0
        row_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        for match in matches:
            # Text before placeholder
            before_text = text[current_pos:match.start()]
            if before_text.strip():
                self._add_text_segment(row_frame, before_text)

            # Input box widget
            placeholder_id = match.group(1)
            blank_data = self._find_blank(placeholder_id)
            if blank_data:
                self._add_input_widget(row_frame, blank_data)

            current_pos = match.end()

        # Text after last placeholder
        after_text = text[current_pos:]
        if after_text.strip():
            self._add_text_segment(row_frame, after_text)

    def _find_blank(self, placeholder_id: str) -> Optional[Dict]:
        """Find blank data by placeholder ID"""
        for blank in self.blanks:
            blank_id = blank.get('answer_id', '')
            if placeholder_id in blank_id or blank_id in placeholder_id:
                return blank
        return None

    def _add_text_segment(self, parent, text: str):
        """Add a text segment with proper text wrapping"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
            text_color=self.get_color('gray_dark'),
            wraplength=650,
            justify="left",
            anchor="w"
        )
        label.pack(side="left", padx=2)

    def _add_input_widget(self, parent, blank_data: Dict):
        """Add an inline input box showing the filled value"""
        filled_text = blank_data.get('text_content', '???')

        # Input-style frame (underlined box)
        input_frame = ctk.CTkFrame(
            parent,
            fg_color=self.get_color('bg_secondary'),
            corner_radius=4,
            border_width=0,
            height=32
        )
        input_frame.pack(side="left", padx=4)

        # Value label with underline effect
        value_label = ctk.CTkLabel(
            input_frame,
            text=filled_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option'], "underline"),
            text_color=EDMENTUM_STYLES['blue_primary']
        )
        value_label.pack(padx=12, pady=6)


# ============================================================================
# HOT TEXT COMPONENT
# ============================================================================

class EdmentumHotText(EdmentumComponent):
    """
    Hot text question - selectable text within passages
    """

    def __init__(self, parent, question_text: str, passage: str,
                 selected_texts: List[str]):
        """
        Args:
            parent: Parent widget
            question_text: The question/instruction text
            passage: The full passage text
            selected_texts: List of text snippets that should be highlighted
        """
        super().__init__(parent)
        self.question_text = question_text
        self.passage = passage
        self.selected_texts = selected_texts

        self._build_ui()

    def _build_ui(self):
        """Build the hot text interface"""
        # Question text
        question_label = ctk.CTkLabel(
            self.parent,
            text=self.question_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
            text_color=self.get_color('gray_dark'),
            wraplength=700,
            justify="left",
            anchor="w"
        )
        question_label.pack(fill="x", pady=(0, 15))

        # Passage container with border
        passage_container = ctk.CTkFrame(
            self.parent,
            fg_color=self.get_color('bg_secondary'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=1,
            border_color=self.get_color('gray_border')
        )
        passage_container.pack(fill="both", expand=True, pady=10)

        # For simplicity, we'll display the passage with selected text highlighted
        # In a full implementation, you'd parse and apply styling to specific spans

        # Create textbox for passage (read-only)
        passage_text = ctk.CTkTextbox(
            passage_container,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option']),
            wrap="word",
            height=200,
            fg_color="transparent"
        )
        passage_text.pack(fill="both", expand=True, padx=15, pady=15)

        # Insert passage text
        passage_text.insert("1.0", self.passage)

        # Highlight selected texts
        for selected in self.selected_texts:
            # Find and highlight each occurrence
            start_idx = "1.0"
            while True:
                pos = passage_text.search(selected, start_idx, stopindex="end")
                if not pos:
                    break
                end_pos = f"{pos}+{len(selected)}c"
                passage_text.tag_add("highlight", pos, end_pos)
                start_idx = end_pos

        # Configure highlight tag with green for correct answers
        # NOTE: CTkTextbox doesn't allow 'font' in tag_config due to scaling conflicts
        # Using only background and foreground for highlighting
        passage_text.tag_config(
            "highlight",
            background="#d4edda",  # Light green for correct selections
            foreground="#155724"   # Dark green text
        )

        # Make read-only
        passage_text.configure(state="disabled")

        # Add large text section showing correct selections
        selections_container = ctk.CTkFrame(
            self.parent,
            fg_color=("#d4edda", "#1a311a"),  # Light/dark green
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=2,
            border_color=EDMENTUM_STYLES['green_correct']
        )
        selections_container.pack(fill="x", pady=(10, 0))

        # Title
        title_label = ctk.CTkLabel(
            selections_container,
            text="✅ Correct Selections:",
            font=(EDMENTUM_STYLES['font_family'], 16, "bold"),
            text_color=EDMENTUM_STYLES['green_correct']
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))

        # Show each selected text in large, bold format
        for selected in self.selected_texts:
            answer_frame = ctk.CTkFrame(
                selections_container,
                fg_color=EDMENTUM_STYLES['green_correct'],
                corner_radius=8,
                height=40
            )
            answer_frame.pack(fill="x", padx=15, pady=5)

            answer_label = ctk.CTkLabel(
                answer_frame,
                text=f"• {selected}",
                font=(EDMENTUM_STYLES['font_family'], 18, "bold"),
                text_color="white",
                wraplength=650,
                anchor="w"
            )
            answer_label.pack(fill="both", expand=True, padx=15, pady=10)

        # Bottom padding
        ctk.CTkLabel(selections_container, text="", height=5).pack()


class EdmentumHotSpot(EdmentumComponent):
    """
    Hot spot question - click specific locations on an image

    NOTE: Bounding boxes are drawn on the screenshot (not in answer container)
    This component only displays the text list of correct locations
    """

    def __init__(self, parent, question_text: str, answers: List[Dict]):
        """
        Args:
            parent: Parent widget (answer container)
            question_text: The question/instruction text
            answers: List of hot_spot answer dicts with text_content
        """
        super().__init__(parent)
        self.question_text = question_text
        self.answers = answers

        self._build_ui()

    def _build_ui(self):
        """Build the hot spot answer interface"""
        # Question text
        question_label = ctk.CTkLabel(
            self.parent,
            text=self.question_text,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_question']),
            text_color=self.get_color('gray_dark'),
            wraplength=700,
            justify="left",
            anchor="w"
        )
        question_label.pack(fill="x", pady=(0, 15))

        # Info box explaining that boxes are on screenshot
        info_container = ctk.CTkFrame(
            self.parent,
            fg_color=self.get_color('bg_info'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=1,
            border_color=EDMENTUM_STYLES['blue_border']
        )
        info_container.pack(fill="x", pady=(0, 15))

        info_label = ctk.CTkLabel(
            info_container,
            text="📍 Green bounding boxes have been drawn on the screenshot showing the correct locations.",
            font=(EDMENTUM_STYLES['font_family'], 12),
            text_color=self.get_color('gray_dark'),
            wraplength=700,
            justify="left"
        )
        info_label.pack(padx=15, pady=10)

        # Correct locations container
        locations_container = ctk.CTkFrame(
            self.parent,
            fg_color=("#d4edda", "#1a311a"),  # Light/dark green
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=2,
            border_color=EDMENTUM_STYLES['green_correct']
        )
        locations_container.pack(fill="x", pady=10)

        # Title
        title_label = ctk.CTkLabel(
            locations_container,
            text="✅ Correct Locations:",
            font=(EDMENTUM_STYLES['font_family'], 16, "bold"),
            text_color=EDMENTUM_STYLES['green_correct']
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))

        # Show each location in large, bold format
        for answer in self.answers:
            text_content = answer.get('text_content', '?')

            location_frame = ctk.CTkFrame(
                locations_container,
                fg_color=EDMENTUM_STYLES['green_correct'],
                corner_radius=8,
                height=40
            )
            location_frame.pack(fill="x", padx=15, pady=5)

            location_label = ctk.CTkLabel(
                location_frame,
                text=f"• {text_content}",
                font=(EDMENTUM_STYLES['font_family'], 18, "bold"),
                text_color="white",
                wraplength=650,
                anchor="w"
            )
            location_label.pack(fill="both", expand=True, padx=15, pady=10)

        # Bottom padding
        ctk.CTkLabel(locations_container, text="", height=5).pack()


# ============================================================================
# QUESTION RENDERER (Routes to appropriate component)
# ============================================================================

class EdmentumQuestionRenderer:
    """
    Main renderer that routes questions to appropriate Edmentum components
    based on the rendering_strategy from AI analysis
    """

    def render_question(self, parent, analysis: dict, question_text: str,
                       answers: list, question_number=None, ui_instance=None) -> bool:
        """
        Render question using appropriate component

        Args:
            parent: Parent widget for rendering
            analysis: initial_analysis dict with rendering_strategy
            question_text: The identified_question text
            answers: List of answer objects
            question_number: Optional question number
            ui_instance: UI instance (needed for hot_spot screenshot annotation)

        Returns:
            True if rendered successfully, False to fallback to standard display
        """
        strategy = analysis.get('rendering_strategy', 'standard_fallback')

        try:
            if strategy == 'edmentum_hot_text':
                return self._render_hot_text(parent, question_text, answers)
            elif strategy == 'edmentum_hot_spot':
                return self._render_hot_spot(parent, question_text, answers, ui_instance)
            elif strategy in ('edmentum_matched_pairs', 'edmentum_matching_pairs'):
                return self._render_matched_pairs(parent, question_text, answers)
            elif strategy == 'edmentum_multiple_choice':
                return self._render_multiple_choice(parent, question_text, answers)
            elif strategy == 'edmentum_multiple_response':
                return self._render_multiple_response(parent, question_text, answers)
            elif strategy == 'edmentum_dropdown':
                return self._render_dropdown(parent, question_text, answers)
            elif strategy == 'standard_fallback':
                return False  # Let standard display handle it
            else:
                print(f"⚠️ Unknown rendering strategy: {strategy}, using fallback")
                return False

        except Exception as e:
            print(f"❌ Edmentum rendering failed for {strategy}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _render_hot_text(self, parent, question_text: str, answers: list) -> bool:
        """Render hot text / text selection questions with green highlighting"""
        try:
            # Extract selected texts from answers
            selected_texts = []
            for answer in answers:
                if answer.get('content_type') == 'text_selection' and answer.get('is_correct_option'):
                    text_content = answer.get('text_content', '')
                    if text_content:
                        selected_texts.append(text_content)

            if not selected_texts:
                print("⚠️ No selected texts found for hot text question")
                return False

            # Create EdmentumHotText component
            # The passage is embedded in question_text, selected_texts are the answers
            EdmentumHotText(parent, question_text, question_text, selected_texts)
            return True

        except Exception as e:
            print(f"❌ Hot text rendering failed: {e}")
            return False

    def _render_hot_spot(self, parent, question_text: str, answers: list, ui_instance=None) -> bool:
        """
        Render hot spot questions with bounding boxes on screenshot

        Args:
            parent: Parent widget for answer display
            question_text: The question text
            answers: List of answer dicts
            ui_instance: UI instance with screenshot annotation methods

        Returns:
            True if rendering succeeded, False otherwise
        """
        try:
            # Extract hot spot answers
            hot_spot_answers = []
            for answer in answers:
                if answer.get('content_type') == 'hot_spot' and answer.get('is_correct_option'):
                    hot_spot_answers.append(answer)

            if not hot_spot_answers:
                print("⚠️ No hot spot answers found")
                return False

            print(f"🎯 Rendering {len(hot_spot_answers)} hot spot answers")

            # Create EdmentumHotSpot component (displays text list in answer container)
            EdmentumHotSpot(parent, question_text, hot_spot_answers)

            # Trigger screenshot annotation if UI instance provided
            if ui_instance and hasattr(ui_instance, '_annotate_screenshot_with_boxes'):
                print("📦 Triggering screenshot annotation...")
                annotated_path = ui_instance._annotate_screenshot_with_boxes(hot_spot_answers)

                if annotated_path and hasattr(ui_instance, '_update_screenshot_from_path'):
                    # Update screenshot display with annotated version
                    ui_instance._update_screenshot_from_path(annotated_path)
                    print("✅ Hot spot rendering complete with bounding boxes")
                else:
                    print("⚠️ Screenshot annotation failed, showing text answers only")

            return True

        except Exception as e:
            print(f"❌ Hot spot rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _render_matched_pairs(self, parent, question_text: str, answers: list) -> bool:
        """Render matching pairs questions"""
        try:
            # Extract pairs from answers
            pairs = []
            for answer in answers:
                if answer.get('content_type') == 'matching_pair':
                    pair_data = answer.get('pair_data', {})
                    if pair_data:
                        pairs.append({
                            'term': pair_data.get('term', ''),
                            'match': pair_data.get('match', ''),
                            'is_correct': answer.get('is_correct_option', True)
                        })

            if not pairs:
                print("⚠️ No matching pairs found")
                return False

            # Create EdmentumMatchedPairs component (note: class name has 'Matched' not 'Matching')
            EdmentumMatchedPairs(parent, question_text, pairs)
            return True

        except Exception as e:
            print(f"❌ Matching pairs rendering failed: {e}")
            return False

    def _render_multiple_choice(self, parent, question_text: str, answers: list) -> bool:
        """Render multiple choice questions"""
        try:
            # Extract options
            options = []
            for answer in answers:
                if answer.get('content_type') == 'multiple_choice_option':
                    # Extract letter from answer_id (e.g., "mc_option_A" -> "A")
                    answer_id = answer.get('answer_id', '')
                    label = answer_id.replace('mc_option_', '').replace('_', ' ')

                    options.append({
                        'label': label if label else str(len(options) + 1),
                        'text': answer.get('text_content', ''),
                        'is_correct': answer.get('is_correct_option', False)
                    })

            if not options:
                print("⚠️ No multiple choice options found")
                return False

            # Create EdmentumMultipleChoice component
            EdmentumMultipleChoice(parent, question_text, options)
            return True

        except Exception as e:
            print(f"❌ Multiple choice rendering failed: {e}")
            return False

    def _render_multiple_response(self, parent, question_text: str, answers: list) -> bool:
        """Render multiple response (select all that apply) questions"""
        # Multiple response is similar to multiple choice but allows multiple selections
        # For display purposes, we can use the same EdmentumMultipleChoice component
        # since it already shows correct answers highlighted
        return self._render_multiple_choice(parent, question_text, answers)

    def _render_dropdown(self, parent, question_text: str, answers: list) -> bool:
        """Render dropdown/cloze questions"""
        try:
            # For now, return False to use standard display
            # Full implementation would create EdmentumDropdown component with inline dropdowns
            # This would require parsing the question_text for placeholders and filling them
            print("ℹ️ Dropdown rendering not fully implemented, using standard display")
            return False
        except Exception as e:
            print(f"❌ Dropdown rendering failed: {e}")
            return False


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'EDMENTUM_STYLES',
    'EdmentumQuestionContainer',
    'EdmentumMultipleChoice',
    'EdmentumMatchedPairs',
    'EdmentumDropdown',
    'EdmentumFillBlank',
    'EdmentumHotText',
    'EdmentumQuestionRenderer',
    'create_circle_badge',
    'get_style'
]
