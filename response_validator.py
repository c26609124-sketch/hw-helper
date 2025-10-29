"""
Response Validator
==================
Validates and auto-fixes AI responses to prevent common issues:
- Multiple answers marked as correct
- No answers marked as correct
- Duplicate or missing labels (A, B, C, D)
- Inconsistent confidence scoring
"""

from typing import Dict, List, Tuple, Optional


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
        """
        Validate and fix multiple choice answers

        Issues fixed:
        1. Ensure exactly 1 answer marked as correct
        2. Ensure unique labels (A, B, C, D)
        3. Ensure unique text content
        4. Fix confidence scoring
        """
        mc_answers = [a for a in answers if a.get('content_type') == 'multiple_choice_option']

        if not mc_answers:
            return answers

        print(f"   Found {len(mc_answers)} multiple choice options")

        # Issue 1: Check how many are marked correct
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

        # Issue 2: Ensure unique and proper labels
        mc_answers = self._fix_labels(mc_answers)

        # Issue 3: Check for duplicate content
        mc_answers = self._check_duplicate_content(mc_answers)

        # Issue 4: Adjust confidence scoring
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
        """
        Auto-select the correct answer based on highest confidence

        Args:
            mc_answers: List of multiple choice answer dicts
            force: If True, clear all is_correct_option flags first

        Returns:
            Fixed mc_answers with exactly one marked correct
        """
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
        """
        Ensure each answer has a unique label (A, B, C, D, E, F...)

        Args:
            mc_answers: List of multiple choice answer dicts

        Returns:
            Fixed mc_answers with proper labels
        """
        expected_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        # Extract current labels
        current_labels = []
        for answer in mc_answers:
            label = answer.get('label', '')
            # Try to extract from answer_id if label is missing
            if not label:
                answer_id = answer.get('answer_id', '')
                if '_' in answer_id:
                    # Try to extract letter from ID like "mc_option_A"
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
        """
        Check if multiple answers have the same text content

        Args:
            mc_answers: List of multiple choice answer dicts

        Returns:
            mc_answers (unmodified, just logs warnings)
        """
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
        """
        Adjust confidence scores to be more meaningful

        Rules:
        - Correct answer should have highest confidence (0.9-1.0)
        - Incorrect answers should have lower confidence (0.0-0.6)

        Args:
            mc_answers: List of multiple choice answer dicts

        Returns:
            Fixed mc_answers with adjusted confidence
        """
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

        # Check if all confidences are too similar (within 0.1 of each other)
        if max(confidences) - min(confidences) < 0.1:
            self.validation_warnings.append(
                f"All confidence scores too similar ({min(confidences):.2f}-{max(confidences):.2f}). Adjusting..."
            )

            # Boost correct answer confidence
            mc_answers[correct_index]['confidence'] = 0.95

            # Lower incorrect answer confidences
            for i, answer in enumerate(mc_answers):
                if i != correct_index:
                    # Vary confidences for incorrect answers
                    answer['confidence'] = 0.2 + (i * 0.1)

            print(f"   → Adjusted confidences: Correct={mc_answers[correct_index]['confidence']:.2f}, Others={[a['confidence'] for i, a in enumerate(mc_answers) if i != correct_index]}")

        return mc_answers

    def _validate_matching_pairs(self, answers: List[Dict]) -> List[Dict]:
        """
        Validate matching pair answers

        Issues checked:
        1. Each pair has both term and match
        2. No duplicate terms
        3. No duplicate matches
        """
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


# Convenience function for quick validation
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


__all__ = ['ResponseValidator', 'validate_response']
