"""
Progressive JSON Parser - Renders formatted UI elements as streaming JSON arrives
Parses incomplete JSON and extracts complete objects for immediate display
"""

import json
import re
from typing import Dict, List, Optional, Tuple


class ProgressiveJSONParser:
    """
    Parses streaming JSON and extracts complete objects as they arrive
    Handles incomplete/malformed JSON gracefully
    """
    
    def __init__(self):
        self.buffer = ""
        self.parsed_data = {
            "initial_analysis": None,
            "metadata": None,
            "identified_question": None,
            "answers": [],
            "status": None
        }
        self.last_rendered_answer_count = 0
        self.initial_analysis_extracted = False
        self.metadata_extracted = False
        
    def add_chunk(self, chunk: str) -> Tuple[bool, Dict]:
        """
        Add a chunk of JSON text and attempt to parse
        
        Returns:
            (has_new_content, extracted_data)
            has_new_content: True if new complete objects found
            extracted_data: Dict with newly complete data
        """
        self.buffer += chunk
        
        # Try to parse the buffer
        newly_complete = {}
        
        # Try full parse first
        try:
            full_data = json.loads(self.buffer)
            # Successfully parsed complete JSON!
            self.parsed_data = full_data
            newly_complete = {
                "complete": True,
                "data": full_data
            }
            return (True, newly_complete)
        except json.JSONDecodeError:
            # Not complete yet, try partial extraction
            pass

        # PRIORITY 0: Extract initial_analysis FIRST if not already extracted
        if not self.initial_analysis_extracted:
            initial_analysis = self._extract_initial_analysis(self.buffer)
            if initial_analysis:
                self.parsed_data["initial_analysis"] = initial_analysis
                self.initial_analysis_extracted = True
                newly_complete["initial_analysis"] = initial_analysis
                print(f"   🔍 Initial analysis extracted: {initial_analysis.get('edmentum_type_name', 'unknown')} with strategy {initial_analysis.get('rendering_strategy', 'unknown')}")

        # PRIORITY 1: Extract metadata if not already extracted
        if not self.metadata_extracted:
            metadata = self._extract_metadata(self.buffer)
            if metadata:
                self.parsed_data["metadata"] = metadata
                self.metadata_extracted = True
                newly_complete["metadata"] = metadata
                print(f"   📋 Metadata extracted: {metadata.get('question_type', 'unknown')} with {metadata.get('total_answers', 0)} answers")

        # Extract identified_question if complete
        if not self.parsed_data.get("identified_question"):
            question = self._extract_field(self.buffer, "identified_question")
            if question:
                self.parsed_data["identified_question"] = question
                newly_complete["identified_question"] = question
        
        # Extract complete answer objects
        new_answers = self._extract_complete_answers(self.buffer)
        if len(new_answers) > self.last_rendered_answer_count:
            # We have new complete answers!
            newly_complete["new_answers"] = new_answers[self.last_rendered_answer_count:]
            self.last_rendered_answer_count = len(new_answers)
        
        has_new = len(newly_complete) > 0
        return (has_new, newly_complete)
    
    def _extract_field(self, json_str: str, field_name: str) -> Optional[str]:
        """Extract a complete string field value if available"""
        # Look for pattern: "field_name": "value"
        pattern = rf'"{field_name}"\s*:\s*"([^"]*)"'
        match = re.search(pattern, json_str)
        if match:
            return match.group(1)
        return None
    
    def _extract_complete_answers(self, json_str: str) -> List[Dict]:
        """
        Extract complete answer objects from partial JSON
        
        Looks for complete {...} objects within the answers array
        """
        answers = []
        
        # Find the answers array start
        answers_start = json_str.find('"answers":')
        if answers_start == -1:
            return answers
        
        # Extract everything after "answers": [
        after_answers = json_str[answers_start:]
        array_start = after_answers.find('[')
        if array_start == -1:
            return answers
        
        # Find complete objects by counting braces
        search_from = array_start + 1
        while True:
            # Find next object start
            obj_start = after_answers.find('{', search_from)
            if obj_start == -1:
                break
            
            # Count braces to find matching close
            brace_count = 0
            obj_end = -1
            for i in range(obj_start, len(after_answers)):
                if after_answers[i] == '{':
                    brace_count += 1
                elif after_answers[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        obj_end = i + 1
                        break
            
            if obj_end > obj_start:
                # Found complete object
                obj_str = after_answers[obj_start:obj_end]
                try:
                    obj_data = json.loads(obj_str)
                    answers.append(obj_data)
                    search_from = obj_end
                except json.JSONDecodeError:
                    # Not actually complete, continue
                    search_from = obj_start + 1
            else:
                # No complete object found
                break
        
        return answers

    def _extract_metadata(self, json_str: str) -> Optional[Dict]:
        """
        Extract complete metadata object if available

        Metadata is expected to be the FIRST field in the JSON response
        Format: "metadata": { "question_type": "...", "total_answers": N, "answer_structure": [...] }
        """
        # Find the metadata field
        metadata_start = json_str.find('"metadata"')
        if metadata_start == -1:
            return None

        # Find the start of the metadata object
        after_metadata = json_str[metadata_start:]
        # Look for the colon after "metadata"
        colon_pos = after_metadata.find(':')
        if colon_pos == -1:
            return None

        # Find the opening brace of the metadata object
        obj_start = after_metadata.find('{', colon_pos)
        if obj_start == -1:
            return None

        # Count braces to find the complete metadata object
        brace_count = 0
        obj_end = -1
        for i in range(obj_start, len(after_metadata)):
            if after_metadata[i] == '{':
                brace_count += 1
            elif after_metadata[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    obj_end = i + 1
                    break

        if obj_end > obj_start:
            # Found complete metadata object
            obj_str = after_metadata[obj_start:obj_end]
            try:
                metadata = json.loads(obj_str)
                return metadata
            except json.JSONDecodeError:
                # Not actually complete or valid JSON
                return None

        return None

    def _extract_initial_analysis(self, json_str: str) -> Optional[Dict]:
        """
        Extract complete initial_analysis object if available

        Initial analysis is expected to be the FIRST field in the JSON response (before metadata)
        Format: "initial_analysis": { "question_type": "...", "edmentum_type_name": "...", ... }
        """
        # Find the initial_analysis field
        analysis_start = json_str.find('"initial_analysis"')
        if analysis_start == -1:
            return None

        # Find the start of the initial_analysis object
        after_analysis = json_str[analysis_start:]
        # Look for the colon after "initial_analysis"
        colon_pos = after_analysis.find(':')
        if colon_pos == -1:
            return None

        # Find the opening brace of the initial_analysis object
        obj_start = after_analysis.find('{', colon_pos)
        if obj_start == -1:
            return None

        # Count braces to find the complete initial_analysis object
        brace_count = 0
        obj_end = -1
        for i in range(obj_start, len(after_analysis)):
            if after_analysis[i] == '{':
                brace_count += 1
            elif after_analysis[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    obj_end = i + 1
                    break

        if obj_end > obj_start:
            # Found complete initial_analysis object
            obj_str = after_analysis[obj_start:obj_end]
            try:
                initial_analysis = json.loads(obj_str)
                return initial_analysis
            except json.JSONDecodeError:
                # Not actually complete or valid JSON
                return None

        return None

    def get_current_state(self) -> Dict:
        """Get currently parsed data"""
        return self.parsed_data