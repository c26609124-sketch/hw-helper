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

    # Blue (Primary)
    'blue_primary': '#0066CC',
    'blue_light': '#E7F3FF',
    'blue_hover': '#D4E9FF',
    'blue_selected': '#CCE5FF',

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
        left_header.pack(side="left", padx=5)

        center_spacer = ctk.CTkFrame(header_frame, fg_color="transparent", width=80)
        center_spacer.pack(side="left")

        right_header = ctk.CTkLabel(
            header_frame,
            text="Matches",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=self.get_color('gray_text'),
            width=250
        )
        right_header.pack(side="left", padx=5)

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
    'create_circle_badge',
    'get_style'
]
