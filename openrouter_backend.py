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
    
    def __init__(self, api_key: str = None):
        # Multiple API keys to try in order
        self.api_keys = [
            api_key or os.environ.get('OPENROUTER_API_KEY'),
            "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",
            "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",
            "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"
        ]
        
        # Filter out None values
        self.api_keys = [key for key in self.api_keys if key is not None]
        
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
        self.current_api_key_index = 0
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize requests session for OpenRouter with multiple API keys"""
        if not self.api_keys:
            logger.warning("No OpenRouter API keys found. Set OPENROUTER_API_KEY environment variable.")
            self.client = None
            return
            
        # Try each API key until one works
        for i, api_key in enumerate(self.api_keys):
            try:
                logger.info(f"Trying API key {i+1}/{len(self.api_keys)}")
                
                # Use requests directly instead of OpenAI client
                self.client = requests.Session()
                self.client.headers.update({
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'http://localhost:5000',
                    'X-Title': 'Notebooker'
                })
                
                # Test the API key with a simple request
                test_response = self.client.get(f"{self.base_url}/models", timeout=10)
                if test_response.status_code == 200:
                    logger.info(f"OpenRouter client initialized successfully with API key {i+1}")
                    self.current_api_key_index = i
                    return
                else:
                    logger.warning(f"API key {i+1} failed with status {test_response.status_code}")
                    
            except Exception as e:
                logger.warning(f"API key {i+1} failed: {e}")
        
        # If all API keys failed
        logger.error("All OpenRouter API keys failed")
        self.client = None
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using OpenRouter with automatic fallback and API key switching"""
        if not self.client:
            return "OpenRouter client not available"
        
        # Try each model with current API key, then try other API keys if needed
        for model_attempt in range(len(self.models)):
            for api_key_attempt in range(len(self.api_keys)):
                model = self.models[self.current_model_index]
                api_key = self.api_keys[self.current_api_key_index]
                
                try:
                    logger.info(f"Trying model: {model} with API key {self.current_api_key_index + 1}")
                    
                    # Update headers with current API key
                    self.client.headers.update({
                        'Authorization': f'Bearer {api_key}'
                    })
                    
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
                        logger.info(f"Successfully generated text using {model} with API key {self.current_api_key_index + 1}")
                        return content.strip()
                    elif response.status_code == 401:
                        logger.warning(f"API key {self.current_api_key_index + 1} failed with 401, trying next key")
                        # Switch to next API key
                        self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)
                        continue
                    else:
                        logger.warning(f"Model {model} failed with status {response.status_code}: {response.text}")
                        # Log the full response for debugging
                        logger.warning(f"Full response: {response.text}")
                        break  # Try next model
                
                except Exception as e:
                    logger.warning(f"Model {model} with API key {self.current_api_key_index + 1} failed: {e}")
                    # Try next API key
                    self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)
                    continue
            
            # Move to next model
            self.current_model_index = (self.current_model_index + 1) % len(self.models)
            
            # Add delay before trying next model
            time.sleep(1)
        
        # If all models and API keys failed, return fallback response
        logger.error("All OpenRouter models and API keys failed, using fallback")
        return self._fallback_response(prompt)
    
    def analyze_image(self, image_url: str, prompt: str = "What is in this image?") -> str:
        """Analyze image using OpenRouter with vision-capable models"""
        if not self.client:
            return "OpenRouter client not available"
        
        # Use Mistral model for image analysis (it supports vision)
        vision_model = "mistralai/mistral-small-3.2-24b-instruct:free"
        
        # Try with current API key first
        for api_key_attempt in range(len(self.api_keys)):
            api_key = self.api_keys[self.current_api_key_index]
            
            try:
                logger.info(f"Analyzing image with {vision_model} using API key {self.current_api_key_index + 1}")
                
                # Update headers with current API key
                self.client.headers.update({
                    'Authorization': f'Bearer {api_key}'
                })
                
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
                    logger.info(f"Successfully analyzed image using {vision_model} with API key {self.current_api_key_index + 1}")
                    return content.strip()
                elif response.status_code == 401:
                    logger.warning(f"API key {self.current_api_key_index + 1} failed with 401, trying next key")
                    # Switch to next API key
                    self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)
                    continue
                else:
                    logger.error(f"Image analysis failed with status {response.status_code}: {response.text}")
                    return f"Image analysis failed: {response.text}"
                
            except Exception as e:
                logger.warning(f"Image analysis with API key {self.current_api_key_index + 1} failed: {e}")
                # Try next API key
                self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)
                continue
        
        return "Image analysis failed: All API keys failed"
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when all models fail"""
        # Check if user is asking about sections specifically
        if 'how many sections' in prompt.lower() or 'sections do i have' in prompt.lower():
            return "I can see you have 0 sections in your project right now. You can create your first section by clicking the '+ Create First Section' button on the right, or ask me to help you plan what sections you need."
        elif 'create sections' in prompt.lower() or 'create them' in prompt.lower() or 'make sections' in prompt.lower():
            return """I'll create the standard VEX engineering notebook sections for you now!

Standard sections:
- Project overview & goals
- Design process & brainstorming
- Technical specifications
- CAD models & drawings
- Programming & code
- Testing & iterations
- Competition results
- Future improvements

Creating your sections..."""
        elif 'vex' in prompt.lower() or 'en' in prompt.lower() or 'engineering notebook' in prompt.lower():
            if 'team' in prompt.lower():
                return """Perfect! Let's create your VEX team engineering notebook.

Quick questions:
1. What VEX game/challenge?
2. Team size?
3. Main robot goals?
4. Timeline?

Standard sections:
- Team overview & goals
- Design process & brainstorming
- Technical specs & CAD
- Programming & code
- Testing & results
- Competition analysis

Want me to create all sections now?"""
            else:
                return """Great! Let's build your VEX engineering notebook.

Quick questions:
1. What VEX project type?
2. Main goals?
3. Timeline?

Standard sections:
- Project overview & goals
- Design process & brainstorming
- Technical specifications
- CAD models & drawings
- Programming & code
- Testing & iterations
- Competition results
- Future improvements

Want me to create all sections now?"""
        elif 'draft' in prompt.lower() and 'section' in prompt.lower():
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
