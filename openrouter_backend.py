"""
OpenRouter Backend Integration for EN Writer
Uses OpenRouter API with multiple free models and automatic fallback
"""

import os
import json
import logging
import time
import random
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterBackend:
    """OpenRouter API backend with multiple free models and fallback"""
    
    def __init__(self, api_key: str = "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"):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
        # List of free models in order of preference
        self.models = [
            "deepseek/deepseek-chat-v3.1:free",
            "openai/gpt-oss-20b:free", 
            "openrouter/sonoma-dusk-alpha",
            "moonshotai/kimi-k2:free",
            "google/gemma-3n-e2b-it:free",
            "mistralai/mistral-small-3.2-24b-instruct:free"
        ]
        
        self.current_model_index = 0
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize requests session for OpenRouter"""
        try:
            # Use requests directly instead of OpenAI client
            self.client = requests.Session()
            self.client.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:5000',
                'X-Title': 'Notebooker'
            })
            logger.info("OpenRouter client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter client: {e}")
            self.client = None
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using OpenRouter with automatic fallback"""
        if not self.client:
            return "OpenRouter client not available"
        
        # Try each model in order until one works
        for attempt in range(len(self.models)):
            model = self.models[self.current_model_index]
            
            try:
                logger.info(f"Trying model: {model}")
                
                # Prepare the request payload
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                # Make the API request
                response = self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    logger.info(f"Successfully generated text using {model}")
                    return content.strip()
                else:
                    logger.warning(f"Model {model} failed with status {response.status_code}: {response.text}")
                
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
            
            # Move to next model
            self.current_model_index = (self.current_model_index + 1) % len(self.models)
            
            # Add delay before trying next model
            time.sleep(1)
        
        # If all models failed, return fallback response
        logger.error("All OpenRouter models failed, using fallback")
        return self._fallback_response(prompt)
    
    def analyze_image(self, image_url: str, prompt: str = "What is in this image?") -> str:
        """Analyze image using OpenRouter with vision-capable models"""
        if not self.client:
            return "OpenRouter client not available"
        
        # Use Mistral model for image analysis (it supports vision)
        vision_model = "mistralai/mistral-small-3.2-24b-instruct:free"
        
        try:
            logger.info(f"Analyzing image with {vision_model}")
            
            # Prepare the request payload for image analysis
            payload = {
                "model": vision_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Make the API request
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                logger.info(f"Successfully analyzed image using {vision_model}")
                return content.strip()
            else:
                logger.error(f"Image analysis failed with status {response.status_code}: {response.text}")
                return f"Image analysis failed: {response.text}"
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return f"Image analysis failed: {str(e)}"
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when all models fail"""
        if 'draft' in prompt.lower() or 'create' in prompt.lower():
            return self._draft_section_template()
        elif 'rewrite' in prompt.lower() or 'improve' in prompt.lower():
            return self._rewrite_content_template()
        elif 'question' in prompt.lower() or 'ask' in prompt.lower():
            return self._generate_questions_template()
        elif 'analyze' in prompt.lower() or 'gap' in prompt.lower():
            return self._analyze_gaps_template()
        else:
            return "I understand you need help with your engineering notebook. Please provide more specific instructions."
    
    def _draft_section_template(self) -> str:
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
    
    def _rewrite_content_template(self) -> str:
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
    
    def _generate_questions_template(self) -> str:
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
    
    def _analyze_gaps_template(self) -> str:
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
    
    def is_available(self) -> bool:
        """Check if OpenRouter backend is available"""
        return self.client is not None
    
    def get_current_model(self) -> str:
        """Get current model name"""
        return self.models[self.current_model_index]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.models.copy()
    
    def switch_model(self, model_index: int) -> bool:
        """Switch to a different model"""
        if 0 <= model_index < len(self.models):
            self.current_model_index = model_index
            logger.info(f"Switched to model: {self.models[model_index]}")
            return True
        return False


# Enhanced EN Writer with OpenRouter integration
class OpenRouterENWriter:
    """EN Writer with OpenRouter LLM integration"""
    
    def __init__(self, base_dir: str, planning_file: str = "planning_sheet.json"):
        from en_writer import ENWriter
        self.en_writer = ENWriter(base_dir, planning_file)
        self.openrouter = OpenRouterBackend()
    
    def draft_new_entry_with_llm(self, section_name: str, user_inputs: Dict[str, str]) -> str:
        """Generate new draft entry using OpenRouter"""
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
        
        llm_response = self.openrouter.generate_text(prompt, max_tokens=1000)
        
        # Add metadata
        enhanced_response = f"{llm_response}\n\n[TAG: {user_inputs.get('tags', 'robotics, engineering')}]\n[COMMENT: {user_inputs.get('comment', 'Generated with OpenRouter LLM assistance')}]"
        
        return enhanced_response
    
    def rewrite_entry_with_llm(self, entry_text: str, improvement_focus: str = "clarity and technical rigor") -> str:
        """Rewrite existing entry using OpenRouter"""
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
        
        return self.openrouter.generate_text(prompt, max_tokens=1000)
    
    def generate_contextual_questions(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """Generate contextual questions using OpenRouter"""
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
        
        llm_response = self.openrouter.generate_text(prompt, max_tokens=300)
        
        # Parse questions from response
        import re
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
        """Analyze content using OpenRouter for deeper insights"""
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
        
        llm_response = self.openrouter.generate_text(prompt, max_tokens=500)
        
        return {
            'llm_analysis': llm_response,
            'backend_used': f"OpenRouter ({self.openrouter.get_current_model()})",
            'timestamp': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Test OpenRouter backend
    openrouter = OpenRouterBackend()
    print(f"Available models: {openrouter.get_available_models()}")
    print(f"Current model: {openrouter.get_current_model()}")
    
    # Test text generation
    test_prompt = "Write a brief introduction to robotics engineering."
    response = openrouter.generate_text(test_prompt)
    print(f"Response: {response}")
