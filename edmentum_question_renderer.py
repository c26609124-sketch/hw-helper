"""
Edmentum Question Renderer
===========================
Renders complete questions with answers in Edmentum visual style.
Uses components from edmentum_components.py to create authentic replicas.
"""

import customtkinter as ctk
from typing import Dict, List, Optional, Any
from edmentum_components import (
    EdmentumQuestionContainer,
    EdmentumMultipleChoice,
    EdmentumMatchedPairs,
    EdmentumDropdown,
    EdmentumFillBlank,
    EdmentumHotText,
    EDMENTUM_STYLES,
    get_style
)


class EdmentumQuestionRenderer:
    """
    Main renderer class that determines question type and renders appropriate visual
    """

    def __init__(self):
        self.supported_strategies = {
            'edmentum_multiple_choice': self._render_multiple_choice,
            'edmentum_matching_pairs': self._render_matching_pairs,
            'edmentum_dropdown': self._render_dropdown_question,
            'edmentum_fill_blank': self._render_fill_blank,
            'edmentum_hot_text': self._render_hot_text,
        }

    def render_question(self,
                       parent_widget: ctk.CTkFrame,
                       analysis: Dict,
                       question_text: str,
                       answers: List[Dict],
                       question_number: Optional[int] = None) -> bool:
        """
        Render a question in Edmentum style

        Args:
            parent_widget: Parent CTkFrame to render into
            analysis: initial_analysis dict from AI response
            question_text: The identified_question text
            answers: List of answer objects
            question_number: Optional question number to display

        Returns:
            True if successfully rendered, False if should fall back to standard display
        """
        try:
            # Get rendering strategy
            strategy = analysis.get('rendering_strategy', 'standard_fallback')

            if strategy == 'standard_fallback' or strategy not in self.supported_strategies:
                # Not an Edmentum type, use fallback
                return False

            # Clear parent widget
            for widget in parent_widget.winfo_children():
                widget.destroy()

            # Create Edmentum container
            container = EdmentumQuestionContainer(parent_widget, question_number)
            content_frame = container.get_content_frame()

            # Route to appropriate renderer
            renderer_func = self.supported_strategies[strategy]
            renderer_func(content_frame, question_text, answers, analysis)

            return True

        except Exception as e:
            print(f"❌ Edmentum rendering error: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # MULTIPLE CHOICE RENDERING
    # ========================================================================

    def _render_multiple_choice(self,
                               parent: ctk.CTkFrame,
                               question_text: str,
                               answers: List[Dict],
                               analysis: Dict):
        """Render a multiple choice question"""

        # Extract options from answers
        options = []
        correct_id = None

        for answer in answers:
            if answer.get('content_type') == 'multiple_choice_option':
                # Determine label (A/B/C/D)
                label = answer.get('label', '')
                if not label:
                    # Try to extract from answer_id like "mc_option_A"
                    answer_id = answer.get('answer_id', '')
                    if '_' in answer_id:
                        label = answer_id.split('_')[-1]

                option_data = {
                    'id': answer.get('answer_id'),
                    'label': label,
                    'text': answer.get('text_content', ''),
                    'is_correct': answer.get('is_correct_option', False),
                    'confidence': answer.get('confidence')
                }
                options.append(option_data)

                if option_data['is_correct']:
                    correct_id = option_data['id']

        # Create multiple choice component
        mc_component = EdmentumMultipleChoice(
            parent,
            question_text=question_text,
            options=options,
            correct_answer_id=correct_id
        )

        # Add explanation section if any answer has one
        self._add_explanation_section(parent, answers)

    # ========================================================================
    # MATCHING PAIRS RENDERING
    # ========================================================================

    def _render_matching_pairs(self,
                              parent: ctk.CTkFrame,
                              question_text: str,
                              answers: List[Dict],
                              analysis: Dict):
        """Render a matching pairs question"""

        # Extract pairs from answers
        pairs = []

        for i, answer in enumerate(answers):
            if answer.get('content_type') == 'matching_pair':
                # Get pair data
                pair_data = answer.get('pair_data', {})

                pair = {
                    'pair_number': i + 1,
                    'term': pair_data.get('term', answer.get('text_content', '')),
                    'match': pair_data.get('match', pair_data.get('match_value', '')),
                    'confidence': answer.get('confidence'),
                    'pair_data': pair_data
                }
                pairs.append(pair)

        # Create matching pairs component
        matching_component = EdmentumMatchedPairs(
            parent,
            question_text=question_text,
            pairs=pairs
        )

        # Add explanation section
        self._add_explanation_section(parent, answers)

    # ========================================================================
    # DROPDOWN RENDERING
    # ========================================================================

    def _render_dropdown_question(self,
                                  parent: ctk.CTkFrame,
                                  question_text: str,
                                  answers: List[Dict],
                                  analysis: Dict):
        """Render a dropdown/cloze question"""

        # Extract dropdown data from answers
        dropdowns = []

        for answer in answers:
            if answer.get('content_type') == 'dropdown_choice':
                # Get dropdown selection data
                dd_data = answer.get('dropdown_selection_data', {})

                dropdown = {
                    'dropdown_id': dd_data.get('dropdown_id', answer.get('answer_id', '')),
                    'selected_text': dd_data.get('selected_text', answer.get('text_content', '')),
                    'confidence': answer.get('confidence')
                }
                dropdowns.append(dropdown)

        # Create dropdown component
        dropdown_component = EdmentumDropdown(
            parent,
            question_text=question_text,
            dropdowns=dropdowns
        )

        # Add note about filled values
        note_frame = ctk.CTkFrame(parent, fg_color="transparent")
        note_frame.pack(fill="x", pady=(15, 5))

        note_label = ctk.CTkLabel(
            note_frame,
            text="✓ Dropdown selections filled above",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label']),
            text_color=EDMENTUM_STYLES['green_correct'],
            anchor="w"
        )
        note_label.pack(anchor="w")

        # Add explanation section
        self._add_explanation_section(parent, answers)

    # ========================================================================
    # FILL IN THE BLANK RENDERING
    # ========================================================================

    def _render_fill_blank(self,
                          parent: ctk.CTkFrame,
                          question_text: str,
                          answers: List[Dict],
                          analysis: Dict):
        """Render a fill-in-the-blank question"""

        # Extract blank data from answers
        blanks = []

        for answer in answers:
            content_type = answer.get('content_type', '')
            # Could be 'direct_answer' or 'fill_in_blank'
            if content_type in ['direct_answer', 'fill_in_blank', 'text_plain']:
                blank = {
                    'answer_id': answer.get('answer_id', ''),
                    'text_content': answer.get('text_content', ''),
                    'confidence': answer.get('confidence')
                }
                blanks.append(blank)

        # Create fill blank component
        fill_blank_component = EdmentumFillBlank(
            parent,
            question_text=question_text,
            blanks=blanks
        )

        # Add note
        note_frame = ctk.CTkFrame(parent, fg_color="transparent")
        note_frame.pack(fill="x", pady=(15, 5))

        note_label = ctk.CTkLabel(
            note_frame,
            text="✓ Blanks filled above",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label']),
            text_color=EDMENTUM_STYLES['green_correct'],
            anchor="w"
        )
        note_label.pack(anchor="w")

        # Add explanation section
        self._add_explanation_section(parent, answers)

    # ========================================================================
    # HOT TEXT RENDERING
    # ========================================================================

    def _render_hot_text(self,
                        parent: ctk.CTkFrame,
                        question_text: str,
                        answers: List[Dict],
                        analysis: Dict):
        """Render a hot text (text selection) question"""

        # Extract selected texts from answers
        selected_texts = []

        for answer in answers:
            if answer.get('content_type') == 'text_selection':
                text = answer.get('text_content', '')
                if text and answer.get('is_correct_option', False):
                    selected_texts.append(text)

        # Parse question_text to separate question from passage
        # Format: "Question text\n\nPASSAGE TEXT"
        parts = question_text.split('\n\n', 1)
        if len(parts) == 2:
            question = parts[0]
            passage = parts[1]
        else:
            # Fallback: use entire question_text as passage if long enough
            if len(question_text) > 200:
                question = "Select the text that answers the question:"
                passage = question_text
            else:
                question = question_text
                passage = self._extract_passage_from_answers(answers)

        # Create hot text component
        hot_text_component = EdmentumHotText(
            parent,
            question_text=question,
            passage=passage,
            selected_texts=selected_texts
        )

        # NO separate answer badges for text selection
        # The passage display with highlights IS the answer

    def _extract_passage_from_answers(self, answers: List[Dict]) -> str:
        """Try to extract a passage from answer data"""
        # Look for longest text content
        longest = ""
        for answer in answers:
            text = answer.get('text_content', '')
            if len(text) > len(longest):
                longest = text
        return longest if len(longest) > 50 else "Passage not found in response data."

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _add_explanation_section(self, parent: ctk.CTkFrame, answers: List[Dict]):
        """Add an explanation section if any answer has one"""
        explanations = []

        for answer in answers:
            explanation = answer.get('explanation', '')
            if explanation and explanation.strip():
                explanations.append({
                    'label': answer.get('label', answer.get('answer_id', '')),
                    'text': explanation
                })

        if not explanations:
            return

        # Create explanation section
        exp_frame = ctk.CTkFrame(
            parent,
            fg_color=get_style('bg_secondary'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=1,
            border_color=get_style('gray_border')
        )
        exp_frame.pack(fill="x", pady=(20, 0))

        # Header
        header = ctk.CTkLabel(
            exp_frame,
            text="📝 Explanation",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=EDMENTUM_STYLES['blue_primary'],
            anchor="w"
        )
        header.pack(fill="x", padx=15, pady=(10, 5))

        # Explanations
        for exp in explanations:
            exp_text = f"{exp['label']}: {exp['text']}" if exp['label'] else exp['text']

            exp_label = ctk.CTkLabel(
                exp_frame,
                text=exp_text,
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option']),
                text_color=get_style('gray_dark'),
                wraplength=650,
                justify="left",
                anchor="w"
            )
            exp_label.pack(fill="x", padx=15, pady=5)

        # Bottom padding
        ctk.CTkFrame(exp_frame, fg_color="transparent", height=5).pack()

    def _add_selections_list(self, parent: ctk.CTkFrame, selections: List[str]):
        """Add a list of selected text snippets"""
        if not selections:
            return

        # Create selections section
        sel_frame = ctk.CTkFrame(
            parent,
            fg_color=get_style('bg_secondary'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=1,
            border_color=get_style('gray_border')
        )
        sel_frame.pack(fill="x", pady=(15, 0))

        # Header
        header = ctk.CTkLabel(
            sel_frame,
            text="✓ Selected Text Passages",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=EDMENTUM_STYLES['green_correct'],
            anchor="w"
        )
        header.pack(fill="x", padx=15, pady=(10, 5))

        # List selections
        for i, text in enumerate(selections, 1):
            sel_item = ctk.CTkFrame(sel_frame, fg_color="transparent")
            sel_item.pack(fill="x", padx=15, pady=3)

            number_label = ctk.CTkLabel(
                sel_item,
                text=f"{i}.",
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option'], "bold"),
                text_color=EDMENTUM_STYLES['blue_primary'],
                width=30
            )
            number_label.pack(side="left")

            text_label = ctk.CTkLabel(
                sel_item,
                text=text,
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_option']),
                text_color=get_style('gray_dark'),
                wraplength=620,
                justify="left",
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True)

        # Bottom padding
        ctk.CTkFrame(sel_frame, fg_color="transparent", height=5).pack()


# ============================================================================
# ANALYSIS DISPLAY COMPONENT
# ============================================================================

class InitialAnalysisDisplay:
    """
    Displays the initial AI analysis section at the top of the response
    """

    @staticmethod
    def create_analysis_display(parent: ctk.CTkFrame, analysis: Dict) -> ctk.CTkFrame:
        """
        Create the initial analysis display

        Args:
            parent: Parent widget
            analysis: initial_analysis dict from AI response

        Returns:
            Frame containing the analysis display
        """
        # Main analysis container
        analysis_frame = ctk.CTkFrame(
            parent,
            fg_color=get_style('blue_light'),
            corner_radius=EDMENTUM_STYLES['border_radius'],
            border_width=1,
            border_color=EDMENTUM_STYLES['blue_primary']
        )
        analysis_frame.pack(fill="x", padx=10, pady=(10, 15))

        # Header
        header_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(12, 8))

        header_label = ctk.CTkLabel(
            header_frame,
            text="🔍 Initial AI Analysis",
            font=(EDMENTUM_STYLES['font_family'], 14, "bold"),
            text_color=EDMENTUM_STYLES['blue_primary'],
            anchor="w"
        )
        header_label.pack(side="left")

        # Content area
        content_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 12))

        # 1. Question Type
        InitialAnalysisDisplay._add_section(
            content_frame,
            "Question Type",
            analysis.get('edmentum_type_name', analysis.get('question_type', 'Unknown'))
        )

        # 2. Placeholder Mapping
        placeholder_mapping = analysis.get('placeholder_mapping', [])
        if placeholder_mapping:
            InitialAnalysisDisplay._add_placeholder_section(content_frame, placeholder_mapping)

        # 3. Visual Elements
        visual_elements = analysis.get('visual_elements', {})
        if visual_elements:
            InitialAnalysisDisplay._add_visual_elements_section(content_frame, visual_elements)

        return analysis_frame

    @staticmethod
    def _add_section(parent: ctk.CTkFrame, title: str, content: str):
        """Add a simple section with title and content"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", pady=4)

        title_label = ctk.CTkLabel(
            section_frame,
            text=f"{title}:",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=EDMENTUM_STYLES['blue_primary'],
            anchor="w",
            width=120
        )
        title_label.pack(side="left")

        content_label = ctk.CTkLabel(
            section_frame,
            text=content,
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label']),
            text_color=get_style('gray_dark'),
            anchor="w"
        )
        content_label.pack(side="left", fill="x", expand=True)

    @staticmethod
    def _add_placeholder_section(parent: ctk.CTkFrame, mappings: List[Dict]):
        """Add placeholder mapping section"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", pady=6)

        title_label = ctk.CTkLabel(
            section_frame,
            text="Placeholders:",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=EDMENTUM_STYLES['blue_primary'],
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 4))

        # List mappings
        for mapping in mappings[:5]:  # Show first 5
            placeholder = mapping.get('placeholder', '')
            type_info = mapping.get('type', '')
            label = mapping.get('label', '')

            mapping_text = f"  • {placeholder} → {type_info}"
            if label:
                mapping_text += f" ({label})"

            mapping_label = ctk.CTkLabel(
                section_frame,
                text=mapping_text,
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'] - 1),
                text_color=get_style('gray_text'),
                anchor="w"
            )
            mapping_label.pack(anchor="w", padx=(15, 0))

        if len(mappings) > 5:
            more_label = ctk.CTkLabel(
                section_frame,
                text=f"  ... and {len(mappings) - 5} more",
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'] - 1),
                text_color=get_style('gray_text'),
                anchor="w"
            )
            more_label.pack(anchor="w", padx=(15, 0))

    @staticmethod
    def _add_visual_elements_section(parent: ctk.CTkFrame, visual_elements: Dict):
        """Add visual elements section"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", pady=6)

        title_label = ctk.CTkLabel(
            section_frame,
            text="Visual Elements:",
            font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'], "bold"),
            text_color=EDMENTUM_STYLES['blue_primary'],
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 4))

        # Create badges for detected elements
        badges_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        badges_frame.pack(fill="x", padx=(15, 0))

        elements = [
            ('has_image', '🖼️ Image'),
            ('has_diagram', '📊 Diagram'),
            ('has_graph', '📈 Graph'),
            ('has_table', '📋 Table')
        ]

        for key, label in elements:
            if visual_elements.get(key, False):
                badge = ctk.CTkFrame(
                    badges_frame,
                    fg_color=get_style('bg_secondary'),
                    corner_radius=4
                )
                badge.pack(side="left", padx=(0, 6), pady=2)

                badge_label = ctk.CTkLabel(
                    badge,
                    text=label,
                    font=(EDMENTUM_STYLES['font_family'], 11),
                    text_color=get_style('gray_dark'),
                    padx=8,
                    pady=3
                )
                badge_label.pack()

        # Interactive elements
        interactive = visual_elements.get('interactive_elements', [])
        if interactive:
            interactive_text = "Interactive: " + ", ".join(interactive)
            interactive_label = ctk.CTkLabel(
                section_frame,
                text=f"  {interactive_text}",
                font=(EDMENTUM_STYLES['font_family'], EDMENTUM_STYLES['font_size_label'] - 1),
                text_color=get_style('gray_text'),
                anchor="w"
            )
            interactive_label.pack(anchor="w", padx=(15, 0), pady=(4, 0))


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'EdmentumQuestionRenderer',
    'InitialAnalysisDisplay'
]
