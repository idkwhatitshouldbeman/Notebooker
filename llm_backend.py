"""
LLM Backend Integration for EN Writer
Supports multiple local LLM backends with fallback options
"""

import os
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""
    
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text based on prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available"""
        pass


class GPT4AllBackend(LLMBackend):
    """GPT4All local LLM backend"""
    
    def __init__(self, model_name: str = "gpt4all-falcon-q4_0.gguf"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize GPT4All model"""
        try:
            from gpt4all import GPT4All
            # Use a smaller model for Render deployment
            self.model = GPT4All("gpt4all-falcon-q4_0.gguf", allow_download=True)
            logger.info(f"GPT4All model {self.model_name} initialized successfully")
        except ImportError:
            logger.warning("GPT4All not available - using fallback mode")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to initialize GPT4All: {e}")
            self.model = None
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using GPT4All"""
        if not self.is_available():
            return "LLM backend not available"
        
        try:
            response = self.model.generate(prompt, max_tokens=max_tokens)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating text with GPT4All: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if GPT4All is available"""
        return self.model is not None


class TransformersBackend(LLMBackend):
    """HuggingFace Transformers backend for local models"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Transformers model"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"Transformers model {self.model_name} initialized successfully")
        except ImportError:
            logger.warning("Transformers not available - using fallback mode")
            self.model = None
            self.tokenizer = None
        except Exception as e:
            logger.error(f"Failed to initialize Transformers model: {e}")
            self.model = None
            self.tokenizer = None
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using Transformers"""
        if not self.is_available():
            return "LLM backend not available"
        
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_tokens,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the original prompt from response
            response = response[len(prompt):].strip()
            return response
        except Exception as e:
            logger.error(f"Error generating text with Transformers: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Transformers backend is available"""
        return self.model is not None and self.tokenizer is not None


class FallbackBackend(LLMBackend):
    """Fallback backend with template-based responses"""
    
    def __init__(self):
        self.templates = {
            'draft_section': self._draft_section_template,
            'rewrite_content': self._rewrite_content_template,
            'generate_questions': self._generate_questions_template,
            'analyze_gaps': self._analyze_gaps_template
        }
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using templates"""
        # Determine the type of request based on prompt content
        if 'draft' in prompt.lower() or 'create' in prompt.lower():
            return self.templates['draft_section'](prompt)
        elif 'rewrite' in prompt.lower() or 'improve' in prompt.lower():
            return self.templates['rewrite_content'](prompt)
        elif 'question' in prompt.lower() or 'ask' in prompt.lower():
            return self.templates['generate_questions'](prompt)
        elif 'analyze' in prompt.lower() or 'gap' in prompt.lower():
            return self.templates['analyze_gaps'](prompt)
        else:
            return "I understand you need help with your engineering notebook. Please provide more specific instructions."
    
    def is_available(self) -> bool:
        """Fallback is always available"""
        return True
    
    def _draft_section_template(self, prompt: str) -> str:
        """Template for drafting new sections"""
        return """
# Section Draft

## Overview
This section covers the key aspects of the topic. The implementation follows standard engineering practices and includes proper documentation.

## Technical Details
- **Specifications**: [Add technical specifications]
- **Requirements**: [List requirements]
- **Constraints**: [Identify constraints]

## Implementation
The implementation approach includes:
1. Design phase
2. Development phase
3. Testing phase
4. Integration phase

## Testing
Testing procedures include:
- Unit testing
- Integration testing
- System testing
- Performance testing

## Results
Results show [describe results and analysis]

## Future Improvements
Potential improvements include:
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

[image 1] - System architecture diagram
[image 2] - Test results visualization

[TAG: robotics, engineering, documentation]
[COMMENT: This is a template draft - please customize with specific details]
"""
    
    def _rewrite_content_template(self, prompt: str) -> str:
        """Template for rewriting content"""
        return """
# Improved Section

## Enhanced Overview
This section has been improved for clarity and technical rigor. The content now follows best practices for engineering documentation.

## Refined Technical Details
The technical specifications have been clarified and expanded to provide comprehensive coverage of the topic.

## Structured Implementation
The implementation section has been reorganized for better readability and includes:
- Clear step-by-step procedures
- Detailed explanations
- Proper formatting

## Comprehensive Testing
Testing procedures have been enhanced with:
- Detailed test cases
- Expected outcomes
- Validation criteria

## Detailed Results
Results analysis has been improved with:
- Quantitative data
- Visual representations
- Statistical analysis

## Strategic Future Improvements
Future improvements are now prioritized and include:
- Short-term goals
- Long-term objectives
- Resource requirements

[TAG: improved, technical, comprehensive]
[COMMENT: Content has been rewritten for better clarity and technical accuracy]
"""
    
    def _generate_questions_template(self, prompt: str) -> str:
        """Template for generating questions"""
        return """
Based on the analysis, here are some targeted questions to help improve your engineering notebook:

1. **Technical Specifications**: Can you provide more detailed technical specifications for the components mentioned?

2. **Implementation Details**: What specific challenges did you encounter during implementation?

3. **Testing Results**: Do you have quantitative data from your testing procedures?

4. **Performance Metrics**: What performance metrics are most important for this system?

5. **Future Development**: What are your priorities for future improvements?

6. **Documentation**: Are there any diagrams or images that would help illustrate the concepts?

Please provide answers to these questions so I can help improve your documentation.
"""
    
    def _analyze_gaps_template(self, prompt: str) -> str:
        """Template for gap analysis"""
        return """
# Gap Analysis Report

## Identified Gaps

### Missing Sections
- [List missing sections that should be included]

### Incomplete Content
- [List sections that need more detail]

### Technical Gaps
- [List areas lacking technical depth]

### Documentation Issues
- [List formatting or clarity issues]

## Recommendations

### Priority 1 (High)
- [Most critical gaps to address]

### Priority 2 (Medium)
- [Important but less critical gaps]

### Priority 3 (Low)
- [Nice-to-have improvements]

## Next Steps
1. Address Priority 1 gaps first
2. Gather additional information for incomplete sections
3. Review and improve technical content
4. Add supporting images and diagrams

This analysis will help guide the improvement of your engineering notebook.
"""


class LLMManager:
    """Manager class for handling multiple LLM backends"""
    
    def __init__(self):
        self.backends = []
        self.current_backend = None
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize available backends in order of preference"""
        # Try GPT4All first
        try:
            gpt4all_backend = GPT4AllBackend()
            if gpt4all_backend.is_available():
                self.backends.append(gpt4all_backend)
                logger.info("GPT4All backend added")
        except Exception as e:
            logger.warning(f"GPT4All not available: {e}")
        
        # Try Transformers as fallback
        try:
            transformers_backend = TransformersBackend()
            if transformers_backend.is_available():
                self.backends.append(transformers_backend)
                logger.info("Transformers backend added")
        except Exception as e:
            logger.warning(f"Transformers not available: {e}")
        
        # Always add fallback backend
        fallback_backend = FallbackBackend()
        self.backends.append(fallback_backend)
        logger.info("Fallback backend added")
        
        # Set current backend to the first available one
        if self.backends:
            self.current_backend = self.backends[0]
            logger.info(f"Current backend: {type(self.current_backend).__name__}")
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using current backend"""
        if not self.current_backend:
            return "No LLM backend available"
        
        return self.current_backend.generate_text(prompt, max_tokens)
    
    def switch_backend(self, backend_index: int) -> bool:
        """Switch to a different backend"""
        if 0 <= backend_index < len(self.backends):
            self.current_backend = self.backends[backend_index]
            logger.info(f"Switched to backend: {type(self.current_backend).__name__}")
            return True
        return False
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backend names"""
        return [type(backend).__name__ for backend in self.backends]
    
    def get_current_backend_name(self) -> str:
        """Get name of current backend"""
        if self.current_backend:
            return type(self.current_backend).__name__
        return "None"


# Enhanced EN Writer with LLM integration
class EnhancedENWriter:
    """Enhanced EN Writer with LLM integration"""
    
    def __init__(self, base_dir: str, planning_file: str = "planning_sheet.json"):
        from en_writer import ENWriter
        self.en_writer = ENWriter(base_dir, planning_file)
        self.llm_manager = LLMManager()
    
    def draft_new_entry_with_llm(self, section_name: str, user_inputs: Dict[str, str]) -> str:
        """Generate new draft entry using LLM"""
        prompt = f"""
        Create a comprehensive engineering notebook section for robotics titled "{section_name}".
        
        User inputs:
        {json.dumps(user_inputs, indent=2)}
        
        Please create a well-structured section with:
        - Clear overview
        - Technical details
        - Implementation approach
        - Testing procedures
        - Results and analysis
        - Future improvements
        - Placeholders for images [image N]
        - Appropriate tags and comments
        
        Format the output as markdown with proper headings and structure.
        """
        
        llm_response = self.llm_manager.generate_text(prompt, max_tokens=1000)
        
        # Add metadata
        enhanced_response = f"{llm_response}\n\n[TAG: {user_inputs.get('tags', 'robotics, engineering')}]\n[COMMENT: {user_inputs.get('comment', 'Generated with LLM assistance')}]"
        
        return enhanced_response
    
    def rewrite_entry_with_llm(self, entry_text: str, improvement_focus: str = "clarity and technical rigor") -> str:
        """Rewrite existing entry using LLM"""
        prompt = f"""
        Rewrite the following engineering notebook content to improve {improvement_focus}:
        
        Original content:
        {entry_text}
        
        Please:
        1. Improve clarity and readability
        2. Enhance technical accuracy
        3. Add missing technical details where appropriate
        4. Improve structure and organization
        5. Maintain the original intent and information
        6. Keep any existing tags and comments
        
        Return the improved version in the same format.
        """
        
        return self.llm_manager.generate_text(prompt, max_tokens=1000)
    
    def generate_contextual_questions(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """Generate contextual questions using LLM"""
        prompt = f"""
        Based on this gap analysis of an engineering notebook for robotics:
        
        {json.dumps(gap_analysis, indent=2)}
        
        Generate 3-5 targeted, specific questions that would help fill the identified gaps.
        Focus on:
        - Technical details needed
        - Missing information
        - Areas needing clarification
        - Documentation improvements
        
        Return the questions as a numbered list.
        """
        
        llm_response = self.llm_manager.generate_text(prompt, max_tokens=300)
        
        # Parse questions from response
        questions = []
        for line in llm_response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Clean up the question
                question = re.sub(r'^\d+\.\s*', '', line)
                question = re.sub(r'^[-*]\s*', '', question)
                if question:
                    questions.append(question)
        
        return questions if questions else ["Please provide more details about the technical implementation."]
    
    def analyze_content_with_llm(self, content: str) -> Dict[str, Any]:
        """Analyze content using LLM for deeper insights"""
        prompt = f"""
        Analyze this engineering notebook content for robotics:
        
        {content}
        
        Provide analysis on:
        1. Technical completeness (what's missing?)
        2. Clarity and readability
        3. Structure and organization
        4. Areas needing improvement
        5. Suggested additions
        
        Return as a structured analysis.
        """
        
        llm_response = self.llm_manager.generate_text(prompt, max_tokens=500)
        
        return {
            'llm_analysis': llm_response,
            'backend_used': self.llm_manager.get_current_backend_name(),
            'timestamp': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Test LLM backends
    llm_manager = LLMManager()
    print(f"Available backends: {llm_manager.get_available_backends()}")
    print(f"Current backend: {llm_manager.get_current_backend_name()}")
    
    # Test text generation
    test_prompt = "Write a brief introduction to robotics engineering."
    response = llm_manager.generate_text(test_prompt)
    print(f"Response: {response}")
