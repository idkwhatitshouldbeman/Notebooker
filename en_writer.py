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

# Import AI service client
from ai_service_client import get_ai_client, get_task_manager, AgentConfig, TaskStatus

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
        """Generate targeted questions for user based on gap analysis using AI service"""
        try:
            # Create prompt context for AI service
            prompt_context = f"""
            As an engineering notebook assistant, analyze the following gap analysis and generate 3-5 targeted questions to help the user improve their documentation:
            
            Gap Analysis:
            - Missing sections: {gap_info.get('missing_sections', [])}
            - Incomplete sections: {gap_info.get('incomplete_sections', [])}
            - Technical gaps: {gap_info.get('technical_gaps', [])}
            - Unclear content: {gap_info.get('unclear_content', [])}
            - Missing images: {gap_info.get('missing_images', [])}
            
            Generate specific, actionable questions that will help the user prioritize and improve their engineering documentation. Focus on robotics and engineering context.
            """
            
            # Use AI service to generate questions
            ai_client = get_ai_client()
            task_manager = get_task_manager()
            
            agent_config = AgentConfig(
                model="deepseek/deepseek-chat-v3.1:free",
                temperature=0.7,
                max_tokens=500
            )
            
            task_id = task_manager.start_task(prompt_context, agent_config)
            
            # Poll for completion
            response = ai_client.poll_task_completion(task_id, max_wait_time=60)
            
            if response.status == TaskStatus.COMPLETED.value and response.agent_reply:
                # Parse AI response to extract questions
                ai_questions = self._parse_ai_questions(response.agent_reply)
                if ai_questions:
                    return ai_questions
            
            # Fallback to template-based questions if AI fails
            logger.warning(f"AI service failed for question generation, using fallback: {response.error}")
            return self._generate_fallback_questions(gap_info)
            
        except Exception as e:
            logger.error(f"Error generating questions with AI service: {e}")
            return self._generate_fallback_questions(gap_info)
    
    def _parse_ai_questions(self, ai_response: str) -> List[str]:
        """Parse AI response to extract individual questions"""
        # Look for numbered questions or bullet points
        questions = []
        
        # Try to find numbered questions (1., 2., etc.)
        numbered_pattern = r'\d+\.\s*([^?\n]*\?)'
        matches = re.findall(numbered_pattern, ai_response)
        if matches:
            questions.extend([match.strip() for match in matches])
        
        # Try to find bullet point questions (-, *, •)
        bullet_pattern = r'[-*•]\s*([^?\n]*\?)'
        matches = re.findall(bullet_pattern, ai_response)
        if matches:
            questions.extend([match.strip() for match in matches])
        
        # If no structured format found, split by sentences ending with ?
        if not questions:
            sentences = re.split(r'[.!?]+', ai_response)
            questions = [s.strip() + '?' for s in sentences if s.strip() and '?' in s]
        
        return questions[:5]  # Limit to 5 questions
    
    def _generate_fallback_questions(self, gap_info: Dict[str, Any]) -> List[str]:
        """Generate fallback questions using template-based approach"""
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
        """Generate new draft entry using AI service"""
        try:
            # Create prompt context for AI service
            title = user_inputs.get('title', 'Section Title')
            overview = user_inputs.get('overview', '')
            technical_details = user_inputs.get('technical_details', '')
            implementation = user_inputs.get('implementation', '')
            testing = user_inputs.get('testing', '')
            results = user_inputs.get('results', '')
            improvements = user_inputs.get('improvements', '')
            tags = user_inputs.get('tags', 'robotics, engineering')
            comment = user_inputs.get('comment', '')
            
            prompt_context = f"""
            As an engineering notebook assistant, create a comprehensive draft entry for a robotics engineering section with the following details:
            
            Title: {title}
            Overview: {overview}
            Technical Details: {technical_details}
            Implementation: {implementation}
            Testing: {testing}
            Results: {results}
            Improvements: {improvements}
            Tags: {tags}
            Comment: {comment}
            
            Create a well-structured engineering notebook entry with:
            1. Clear heading hierarchy
            2. Technical rigor appropriate for robotics
            3. Professional engineering documentation style
            4. Placeholder references for images [image N]
            5. Proper sections: Overview, Technical Details, Implementation, Testing, Results, Future Improvements
            
            Focus on clarity, technical accuracy, and professional engineering standards.
            """
            
            # Use AI service to generate draft
            ai_client = get_ai_client()
            task_manager = get_task_manager()
            
            agent_config = AgentConfig(
                model="deepseek/deepseek-chat-v3.1:free",
                temperature=0.7,
                max_tokens=1500
            )
            
            task_id = task_manager.start_task(prompt_context, agent_config)
            
            # Poll for completion
            response = ai_client.poll_task_completion(task_id, max_wait_time=120)
            
            if response.status == TaskStatus.COMPLETED.value and response.agent_reply:
                # Clean up and format the AI response
                draft_content = self._format_ai_draft(response.agent_reply, user_inputs)
                return draft_content
            
            # Fallback to template-based generation if AI fails
            logger.warning(f"AI service failed for draft generation, using fallback: {response.error}")
            return self._generate_fallback_draft(user_inputs)
            
        except Exception as e:
            logger.error(f"Error generating draft with AI service: {e}")
            return self._generate_fallback_draft(user_inputs)
    
    def _format_ai_draft(self, ai_response: str, user_inputs: Dict[str, str]) -> str:
        """Format AI response into proper draft structure"""
        # Ensure proper heading structure
        if not ai_response.startswith('#'):
            title = user_inputs.get('title', 'Section Title')
            ai_response = f"# {title}\n\n{ai_response}"
        
        # Add image placeholders if not present
        if '[image' not in ai_response:
            ai_response += "\n\n[image 1] - System architecture diagram\n[image 2] - Implementation flowchart"
        
        # Add tags and comment if not present
        tags = user_inputs.get('tags', 'robotics, engineering')
        comment = user_inputs.get('comment', 'Generated using AI assistance')
        
        if '[TAG:' not in ai_response:
            ai_response += f"\n\n[TAG: {tags}]"
        if '[COMMENT:' not in ai_response:
            ai_response += f"\n[COMMENT: {comment}]"
        
        return ai_response.strip()
    
    def _generate_fallback_draft(self, user_inputs: Dict[str, str]) -> str:
        """Generate fallback draft using template-based approach"""
        title = user_inputs.get('title', 'Section Title')
        overview = user_inputs.get('overview', '')
        technical_details = user_inputs.get('technical_details', '')
        implementation = user_inputs.get('implementation', '')
        testing = user_inputs.get('testing', '')
        results = user_inputs.get('results', '')
        improvements = user_inputs.get('improvements', '')
        tags = user_inputs.get('tags', 'robotics, engineering')
        comment = user_inputs.get('comment', '')
        
        # Generate contextual content based on section type
        section_type = self._detect_section_type(title, overview)
        contextual_content = self._generate_contextual_content(section_type, user_inputs)
        
        template = f"""# {title}

## Overview
{overview or contextual_content.get('overview', 'This section provides a comprehensive overview of the {title.lower()} component.')}

## Technical Details
{technical_details or contextual_content.get('technical_details', 'Technical specifications and implementation details will be documented here.')}

## Implementation
{implementation or contextual_content.get('implementation', 'Implementation approach and methodology will be described in this section.')}

## Testing
{testing or contextual_content.get('testing', 'Testing procedures, test cases, and validation results will be documented here.')}

## Results
{results or contextual_content.get('results', 'Results, analysis, and performance metrics will be presented in this section.')}

## Future Improvements
{improvements or contextual_content.get('improvements', 'Future enhancements and optimization opportunities will be outlined here.')}

[image 1] - {user_inputs.get('image1_caption', 'System architecture diagram')}
[image 2] - {user_inputs.get('image2_caption', 'Implementation flowchart')}

[TAG: {tags}]
[COMMENT: {comment or 'Generated using template-based AI assistance. Enhanced content available when AI service is deployed.'}]
"""
        return template.strip()
    
    def _detect_section_type(self, title: str, overview: str) -> str:
        """Detect the type of engineering section based on title and overview"""
        title_lower = title.lower()
        overview_lower = overview.lower()
        
        if any(word in title_lower for word in ['hardware', 'sensor', 'actuator', 'motor', 'circuit']):
            return 'hardware'
        elif any(word in title_lower for word in ['software', 'code', 'algorithm', 'program']):
            return 'software'
        elif any(word in title_lower for word in ['control', 'pid', 'feedback', 'loop']):
            return 'control'
        elif any(word in title_lower for word in ['test', 'validation', 'verification']):
            return 'testing'
        elif any(word in title_lower for word in ['result', 'analysis', 'performance']):
            return 'analysis'
        else:
            return 'general'
    
    def _generate_contextual_content(self, section_type: str, user_inputs: Dict[str, str]) -> Dict[str, str]:
        """Generate contextual content based on section type"""
        content_templates = {
            'hardware': {
                'overview': 'This section documents the hardware components, specifications, and physical implementation of the system.',
                'technical_details': 'Hardware specifications, component selection criteria, and technical requirements will be detailed here.',
                'implementation': 'Physical assembly, wiring diagrams, and hardware integration procedures will be documented.',
                'testing': 'Hardware testing procedures, component validation, and performance verification will be outlined.',
                'results': 'Hardware performance metrics, test results, and component reliability data will be presented.',
                'improvements': 'Hardware optimization opportunities, component upgrades, and design improvements will be suggested.'
            },
            'software': {
                'overview': 'This section covers the software architecture, algorithms, and code implementation.',
                'technical_details': 'Software architecture, design patterns, and technical specifications will be documented.',
                'implementation': 'Code structure, algorithms, and implementation details will be described.',
                'testing': 'Software testing procedures, unit tests, and integration testing will be outlined.',
                'results': 'Software performance metrics, execution times, and functionality validation will be presented.',
                'improvements': 'Code optimization, algorithm improvements, and software enhancements will be suggested.'
            },
            'control': {
                'overview': 'This section documents the control system design, algorithms, and implementation.',
                'technical_details': 'Control theory, mathematical models, and system dynamics will be detailed.',
                'implementation': 'Control algorithm implementation, tuning procedures, and system integration will be described.',
                'testing': 'Control system testing, stability analysis, and performance validation will be outlined.',
                'results': 'Control performance metrics, response characteristics, and system behavior will be presented.',
                'improvements': 'Control algorithm optimization, parameter tuning, and system enhancements will be suggested.'
            },
            'testing': {
                'overview': 'This section outlines the testing methodology, procedures, and validation approach.',
                'technical_details': 'Test specifications, requirements, and acceptance criteria will be documented.',
                'implementation': 'Test setup, procedures, and execution methodology will be described.',
                'testing': 'Test execution, data collection, and validation procedures will be detailed.',
                'results': 'Test results, analysis, and validation outcomes will be presented.',
                'improvements': 'Testing methodology improvements, additional test cases, and validation enhancements will be suggested.'
            },
            'analysis': {
                'overview': 'This section presents the analysis of results, performance evaluation, and system assessment.',
                'technical_details': 'Analysis methodology, metrics, and evaluation criteria will be documented.',
                'implementation': 'Data analysis procedures, tools, and techniques will be described.',
                'testing': 'Validation of analysis results and verification procedures will be outlined.',
                'results': 'Analysis results, findings, and conclusions will be presented.',
                'improvements': 'Analysis methodology improvements, additional metrics, and enhanced evaluation techniques will be suggested.'
            },
            'general': {
                'overview': 'This section provides a comprehensive overview of the topic and its relevance to the project.',
                'technical_details': 'Technical specifications, requirements, and implementation details will be documented.',
                'implementation': 'Implementation approach, methodology, and procedures will be described.',
                'testing': 'Testing procedures, validation methods, and verification approaches will be outlined.',
                'results': 'Results, findings, and analysis will be presented.',
                'improvements': 'Future improvements, optimizations, and enhancements will be suggested.'
            }
        }
        
        return content_templates.get(section_type, content_templates['general'])
    
    def rewrite_entry(self, entry_text: str) -> str:
        """Rewrite existing entry for clarity and technical rigor using AI service"""
        try:
            # Create prompt context for AI service
            prompt_context = f"""
            As an engineering notebook assistant, rewrite the following engineering documentation to improve clarity, technical rigor, and professional presentation:
            
            Original Text:
            {entry_text}
            
            Please rewrite this content to:
            1. Improve clarity and readability
            2. Enhance technical rigor and precision
            3. Ensure proper engineering documentation standards
            4. Maintain all technical information while improving presentation
            5. Fix any formatting issues
            6. Add appropriate technical terminology
            7. Ensure proper heading hierarchy and structure
            
            Focus on making this a professional, clear, and technically accurate engineering document suitable for robotics projects.
            """
            
            # Use AI service to rewrite content
            ai_client = get_ai_client()
            task_manager = get_task_manager()
            
            agent_config = AgentConfig(
                model="deepseek/deepseek-chat-v3.1:free",
                temperature=0.5,  # Lower temperature for more consistent rewriting
                max_tokens=2000
            )
            
            task_id = task_manager.start_task(prompt_context, agent_config)
            
            # Poll for completion
            response = ai_client.poll_task_completion(task_id, max_wait_time=120)
            
            if response.status == TaskStatus.COMPLETED.value and response.agent_reply:
                # Clean up and format the AI response
                rewritten_content = self._format_ai_rewrite(response.agent_reply, entry_text)
                return rewritten_content
            
            # Fallback to template-based rewriting if AI fails
            logger.warning(f"AI service failed for rewrite, using fallback: {response.error}")
            return self._generate_fallback_rewrite(entry_text)
            
        except Exception as e:
            logger.error(f"Error rewriting with AI service: {e}")
            return self._generate_fallback_rewrite(entry_text)
    
    def _format_ai_rewrite(self, ai_response: str, original_text: str) -> str:
        """Format AI rewrite response"""
        # Ensure the response maintains the original structure
        if not ai_response.strip():
            return original_text
        
        # Clean up any extra formatting
        rewritten = ai_response.strip()
        
        # Ensure proper line breaks
        rewritten = re.sub(r'\n\s*\n\s*\n', '\n\n', rewritten)
        
        return rewritten
    
    def _generate_fallback_rewrite(self, entry_text: str) -> str:
        """Generate fallback rewrite using template-based approach"""
        improved_text = entry_text
        
        # Fix common formatting issues
        improved_text = re.sub(r'\n\s*\n\s*\n', '\n\n', improved_text)  # Remove excessive line breaks
        improved_text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', improved_text)  # Add paragraph breaks
        
        # Enhance technical content
        improved_text = self._enhance_technical_content(improved_text)
        
        # Improve structure and clarity
        improved_text = self._improve_structure(improved_text)
        
        # Add technical rigor
        improved_text = self._add_technical_rigor(improved_text)
        
        return improved_text
    
    def _enhance_technical_content(self, text: str) -> str:
        """Enhance technical content with better descriptions"""
        enhancements = {
            r'\bTODO\b': '**TODO:**',
            r'\bFIXME\b': '**FIXME:**',
            r'\bTBD\b': '**To Be Determined:**',
            r'\bXXX\b': '**Note:**',
            r'\b\.\.\.\b': '**[Additional details to be added]**',
            r'\b(?:implement|implementation)\b': '**Implementation:**',
            r'\b(?:test|testing)\b': '**Testing:**',
            r'\b(?:result|results)\b': '**Results:**',
            r'\b(?:improve|improvement)\b': '**Improvements:**'
        }
        
        for pattern, replacement in enhancements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _improve_structure(self, text: str) -> str:
        """Improve the structure and organization of the text"""
        # Ensure proper heading hierarchy
        if not text.startswith('#'):
            first_line = text.split('\n')[0]
            text = f"# {first_line}\n\n{text}"
        
        # Add missing sections if they don't exist
        sections = ['Overview', 'Technical Details', 'Implementation', 'Testing', 'Results', 'Improvements']
        for section in sections:
            if f"## {section}" not in text and f"# {section}" not in text:
                text += f"\n\n## {section}\n[Content to be added]"
        
        return text
    
    def _add_technical_rigor(self, text: str) -> str:
        """Add technical rigor and engineering standards"""
        # Add technical comment if content seems incomplete
        if len(text.strip()) < 200:
            text += "\\n\\n**[Technical Note:]** This section requires additional technical details, specifications, and implementation information to meet engineering documentation standards."
        
        # Add improvement suggestions
        if 'improvement' not in text.lower() and 'future' not in text.lower():
            text += "\\n\\n## Future Improvements\\n[Future enhancements and optimizations to be documented]"
        
        return text
    
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
