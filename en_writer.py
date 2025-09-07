"""
Agentic Engineering Notebook (EN) Writer for Robotics
A modular system for managing and improving engineering documentation
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ENWriter:
    """Main class for the Engineering Notebook Writer agent"""
    
    def __init__(self, base_dir: str, planning_file: str = "planning_sheet.json"):
        self.base_dir = Path(base_dir)
        self.planning_file = self.base_dir / planning_file
        self.sections = {}
        self.planning_data = self._load_planning_sheet()
        self.activity_log = []
        
    def _load_planning_sheet(self) -> Dict[str, Any]:
        """Load or create planning sheet"""
        if self.planning_file.exists():
            try:
                with open(self.planning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading planning sheet: {e}")
                return self._create_default_planning()
        else:
            return self._create_default_planning()
    
    def _create_default_planning(self) -> Dict[str, Any]:
        """Create default planning sheet structure"""
        return {
            "sections_needing_work": [],
            "user_questions": [],
            "decisions_taken": [],
            "drafts_produced": [],
            "last_updated": datetime.now().isoformat(),
            "current_focus": None,
            "completed_sections": []
        }
    
    def load_en_sections(self, dir_path: str) -> Dict[str, str]:
        """Load and parse all EN files from directory"""
        sections = {}
        en_dir = Path(dir_path)
        
        if not en_dir.exists():
            logger.error(f"Directory {dir_path} does not exist")
            return sections
            
        for file_path in en_dir.glob("*.txt"):
            try:
                content = self.parse_en_file(str(file_path))
                section_name = file_path.stem
                sections[section_name] = content
                logger.info(f"Loaded section: {section_name}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                
        self.sections = sections
        return sections
    
    def parse_en_file(self, filepath: str) -> str:
        """Parse individual EN file and extract content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata and content
            # Look for tags and comments in format [TAG: value] or [COMMENT: text]
            tags = re.findall(r'\[TAG:\s*([^\]]+)\]', content)
            comments = re.findall(r'\[COMMENT:\s*([^\]]+)\]', content)
            images = re.findall(r'\[image\s+(\d+)\]', content, re.IGNORECASE)
            
            # Store metadata for later use
            metadata = {
                'tags': tags,
                'comments': comments,
                'images': images,
                'filepath': filepath,
                'last_modified': os.path.getmtime(filepath)
            }
            
            # Clean content for processing (remove metadata markers)
            clean_content = re.sub(r'\[TAG:\s*[^\]]+\]', '', content)
            clean_content = re.sub(r'\[COMMENT:\s*[^\]]+\]', '', clean_content)
            
            return clean_content.strip()
            
        except Exception as e:
            logger.error(f"Error parsing file {filepath}: {e}")
            return ""
    
    def update_planning_sheet(self, updates: Dict[str, Any]) -> None:
        """Update planning sheet with new information"""
        try:
            self.planning_data.update(updates)
            self.planning_data['last_updated'] = datetime.now().isoformat()
            
            # Save to file
            with open(self.planning_file, 'w', encoding='utf-8') as f:
                json.dump(self.planning_data, f, indent=2, ensure_ascii=False)
                
            logger.info("Planning sheet updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating planning sheet: {e}")
    
    def analyze_sections_for_gaps(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Analyze sections for completeness and identify gaps"""
        gap_analysis = {
            'incomplete_sections': [],
            'missing_sections': [],
            'unclear_content': [],
            'missing_images': [],
            'technical_gaps': []
        }
        
        # Define expected sections for robotics EN
        expected_sections = [
            'system_overview', 'hardware_design', 'software_architecture',
            'control_systems', 'sensors', 'actuators', 'testing_procedures',
            'results_analysis', 'future_improvements', 'references'
        ]
        
        # Check for missing sections
        for section in expected_sections:
            if section not in sections:
                gap_analysis['missing_sections'].append(section)
        
        # Analyze existing sections
        for section_name, content in sections.items():
            if not content or len(content.strip()) < 100:
                gap_analysis['incomplete_sections'].append(section_name)
            
            # Check for technical completeness
            if self._has_technical_gaps(content):
                gap_analysis['technical_gaps'].append(section_name)
            
            # Check for unclear content
            if self._is_content_unclear(content):
                gap_analysis['unclear_content'].append(section_name)
            
            # Check for missing images
            if self._needs_images(content):
                gap_analysis['missing_images'].append(section_name)
        
        return gap_analysis
    
    def _has_technical_gaps(self, content: str) -> bool:
        """Check if content has technical gaps"""
        # Look for placeholder text or incomplete technical details
        placeholders = ['TODO', 'TBD', 'FIXME', 'XXX', '...']
        return any(placeholder in content.upper() for placeholder in placeholders)
    
    def _is_content_unclear(self, content: str) -> bool:
        """Check if content is unclear or needs clarification"""
        # Simple heuristics for unclear content
        unclear_indicators = [
            'unclear', 'confusing', 'needs clarification', 'not sure',
            'maybe', 'possibly', 'might be', 'could be'
        ]
        return any(indicator in content.lower() for indicator in unclear_indicators)
    
    def _needs_images(self, content: str) -> bool:
        """Check if content would benefit from images"""
        # Look for technical descriptions that typically need diagrams
        image_indicators = [
            'diagram', 'schematic', 'flowchart', 'architecture',
            'circuit', 'mechanical design', 'assembly', 'layout'
        ]
        return any(indicator in content.lower() for indicator in image_indicators)
    
    def generate_user_questions(self, gap_info: Dict[str, Any]) -> List[str]:
        """Generate targeted questions for user based on gap analysis"""
        questions = []
        
        # Questions for missing sections
        if gap_info['missing_sections']:
            questions.append(f"Which of these sections would you like to prioritize: {', '.join(gap_info['missing_sections'])}?")
        
        # Questions for incomplete sections
        if gap_info['incomplete_sections']:
            questions.append(f"These sections need more content: {', '.join(gap_info['incomplete_sections'])}. What additional information should I include?")
        
        # Questions for technical gaps
        if gap_info['technical_gaps']:
            questions.append(f"These sections have technical gaps: {', '.join(gap_info['technical_gaps'])}. Can you provide more technical details?")
        
        # Questions for unclear content
        if gap_info['unclear_content']:
            questions.append(f"These sections need clarification: {', '.join(gap_info['unclear_content'])}. What specific aspects need to be clearer?")
        
        # Questions for missing images
        if gap_info['missing_images']:
            questions.append(f"These sections would benefit from images: {', '.join(gap_info['missing_images'])}. Do you have diagrams or photos to include?")
        
        return questions
    
    def draft_new_entry(self, section_content: str, user_inputs: Dict[str, str]) -> str:
        """Generate new draft entry based on section content and user inputs"""
        # This would integrate with LLM backend
        # For now, return a structured template
        
        template = f"""
# {user_inputs.get('title', 'Section Title')}

## Overview
{user_inputs.get('overview', 'Provide overview of this section')}

## Technical Details
{user_inputs.get('technical_details', 'Add technical specifications and implementation details')}

## Implementation
{user_inputs.get('implementation', 'Describe implementation approach')}

## Testing
{user_inputs.get('testing', 'Describe testing procedures and results')}

## Results
{user_inputs.get('results', 'Present results and analysis')}

## Future Improvements
{user_inputs.get('improvements', 'Suggest future improvements')}

[image 1] - {user_inputs.get('image1_caption', 'Add image caption')}
[image 2] - {user_inputs.get('image2_caption', 'Add image caption')}

[TAG: {user_inputs.get('tags', 'robotics, engineering')}]
[COMMENT: {user_inputs.get('comment', 'Add any additional notes')}]
"""
        return template.strip()
    
    def rewrite_entry(self, entry_text: str) -> str:
        """Rewrite existing entry for clarity and technical rigor"""
        # This would integrate with LLM backend for content improvement
        # For now, return the original text with some basic improvements
        
        # Basic text improvements
        improved_text = entry_text
        
        # Fix common formatting issues
        improved_text = re.sub(r'\n\s*\n\s*\n', '\n\n', improved_text)  # Remove excessive line breaks
        improved_text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', improved_text)  # Add paragraph breaks
        
        return improved_text
    
    def save_en_files(self, updated_sections: Dict[str, str]) -> None:
        """Save updated EN files to disk"""
        try:
            for section_name, content in updated_sections.items():
                file_path = self.base_dir / f"{section_name}.txt"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Saved section: {section_name}")
                
        except Exception as e:
            logger.error(f"Error saving EN files: {e}")
    
    def log_agent_activity(self, activity_log_filepath: str, log_entry: Dict[str, Any]) -> None:
        """Log agent activity for tracking and debugging"""
        try:
            log_entry['timestamp'] = datetime.now().isoformat()
            self.activity_log.append(log_entry)
            
            # Save to file
            with open(activity_log_filepath, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')
                
            logger.info(f"Activity logged: {log_entry.get('action', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current status summary"""
        return {
            'total_sections': len(self.sections),
            'sections_needing_work': len(self.planning_data.get('sections_needing_work', [])),
            'completed_sections': len(self.planning_data.get('completed_sections', [])),
            'pending_questions': len(self.planning_data.get('user_questions', [])),
            'last_updated': self.planning_data.get('last_updated', 'Never'),
            'current_focus': self.planning_data.get('current_focus', 'None')
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize EN Writer
    en_writer = ENWriter("./en_files")
    
    # Load sections
    sections = en_writer.load_en_sections("./en_files")
    
    # Analyze for gaps
    gap_analysis = en_writer.analyze_sections_for_gaps(sections)
    
    # Generate questions
    questions = en_writer.generate_user_questions(gap_analysis)
    
    print("Gap Analysis:", gap_analysis)
    print("Generated Questions:", questions)
    print("Status Summary:", en_writer.get_status_summary())
