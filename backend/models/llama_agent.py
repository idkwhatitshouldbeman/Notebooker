"""
FLAN-T5 Small Agent Implementation for Autonomous Workflows
Based on Google's FLAN-T5 model - excellent for reasoning and multi-step tasks
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    T5Tokenizer,
    T5ForConditionalGeneration
)
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = structlog.get_logger()

class FlanT5Agent:
    """
    Autonomous agent powered by FLAN-T5 Small for multi-step workflows
    FLAN-T5 is excellent for reasoning, translation, and text generation tasks
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_initialized = False
        
        # Agent configuration
        self.temperature = 0.7
        self.max_tokens = 1000
        self.stop_sequences = []
        self.top_p = 0.9
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0
        
        # Task processing state
        self.current_task_id = None
        self.conversation_history = []
        self.tool_results = {}
        
    async def initialize(self):
        """Initialize the FLAN-T5 model and tokenizer with error handling"""
        if self.is_initialized:
            logger.info("🔧 FLAN-T5 model already initialized")
            return
            
        try:
            logger.info("🚀 Initializing FLAN-T5 Small model", device=self.device)
            
            # Load tokenizer - FLAN-T5 uses T5 tokenizer
            logger.info("📥 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR,
                trust_remote_code=True
            )
            logger.info("✅ Tokenizer loaded successfully")
            
            # Load model - FLAN-T5 is a sequence-to-sequence model
            logger.info("📥 Loading FLAN-T5 model...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            logger.info("✅ Model loaded successfully")
            
            # Move model to device if not using device_map
            if self.device == "cuda" and not hasattr(self.model, 'hf_device_map'):
                logger.info("🔄 Moving model to CUDA device...")
                self.model = self.model.to(self.device)
                logger.info("✅ Model moved to CUDA")
            
            self.is_initialized = True
            logger.info("🎉 FLAN-T5 model initialized successfully", 
                       model_size="80M parameters", 
                       download_size="300MB")
            
        except Exception as e:
            logger.error("❌ Failed to initialize FLAN-T5 model", error=str(e))
            logger.error("🔧 Attempting fallback initialization...")
            
            # Fallback: try with minimal configuration
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "google/flan-t5-small",
                    trust_remote_code=True
                )
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    "google/flan-t5-small",
                    torch_dtype=torch.float32,
                    trust_remote_code=True
                )
                self.is_initialized = True
                logger.info("✅ Fallback initialization successful")
            except Exception as fallback_error:
                logger.error("❌ Fallback initialization also failed", error=str(fallback_error))
                # Don't raise - allow service to continue without AI
                self.is_initialized = False
    
    def configure(self, **kwargs):
        """Configure agent parameters"""
        self.temperature = kwargs.get('temperature', self.temperature)
        self.max_tokens = kwargs.get('max_tokens', self.max_tokens)
        self.stop_sequences = kwargs.get('stop_sequences', self.stop_sequences)
        self.top_p = kwargs.get('top_p', self.top_p)
        self.frequency_penalty = kwargs.get('frequency_penalty', self.frequency_penalty)
        self.presence_penalty = kwargs.get('presence_penalty', self.presence_penalty)
        
        logger.info("Agent configured", 
                   temperature=self.temperature,
                   max_tokens=self.max_tokens)
    
    async def process_task(self, prompt_context: str, task_context: Dict[str, Any], 
                          external_tools: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an agentic task with autonomous multi-step workflows using FLAN-T5
        """
        logger.info("🤖 Starting AI task processing", task_id=task_context.get("task_id"))
        
        if not self.is_initialized:
            logger.info("🔧 Model not initialized, attempting initialization...")
            await self.initialize()
        
        self.current_task_id = task_context.get("task_id")
        self.conversation_history = task_context.get("conversation_history", [])
        
        try:
            logger.info("🚀 Starting agentic task processing with FLAN-T5", task_id=self.current_task_id)
            
            # Check if model is available
            if not self.is_initialized or not self.model:
                logger.warning("⚠️ AI model not available, using fallback response")
                return {
                    "status": "completed",
                    "agent_reply": f"I'm here to help with your engineering project! Based on your request: '{prompt_context}', I can assist with technical documentation, project planning, and content analysis. However, my AI model is currently unavailable, so I'm providing this basic response. Please try again later when the AI service is fully loaded.",
                    "next_step": {
                        "action": "complete",
                        "instructions": "Task completed with fallback response"
                    },
                    "logs": "AI model not available - using fallback",
                    "tokens_used": 0
                }
            
            # FLAN-T5 excels at reasoning tasks, so we'll structure the prompt accordingly
            logger.info("📝 Building reasoning prompt...")
            reasoning_prompt = self._build_reasoning_prompt(prompt_context, external_tools)
            logger.info("✅ Reasoning prompt built")
            
            # Generate the main response using FLAN-T5's reasoning capabilities
            logger.info("🧠 Generating AI response...")
            main_response = await self._generate_reasoning_response(reasoning_prompt)
            logger.info("✅ AI response generated")
            
            # If external tools are available, try to use them
            if external_tools:
                logger.info("🔧 Enhancing response with external tools...")
                enhanced_response = await self._enhance_with_tools(main_response, external_tools)
                logger.info("✅ Response enhanced with tools")
            else:
                enhanced_response = main_response
                logger.info("ℹ️ No external tools available, using base response")
            
            # Generate final structured response
            logger.info("📋 Generating final structured response...")
            final_response = await self._generate_final_response(enhanced_response, prompt_context)
            logger.info("✅ Final response generated")
            
            logger.info("🎉 Task processing completed successfully")
            return {
                "status": "completed",
                "agent_reply": final_response,
                "next_step": {
                    "action": "complete",
                    "instructions": "Task completed successfully using FLAN-T5 reasoning"
                },
                "logs": self._format_logs(),
                "tokens_used": self._count_tokens(prompt_context + final_response)
            }
            
        except Exception as e:
            logger.error("❌ Task processing failed", task_id=self.current_task_id, error=str(e))
            return {
                "status": "failed",
                "agent_reply": f"I encountered an error while processing your request: {str(e)}. Please try again or contact support if the issue persists.",
                "next_step": {
                    "action": "retry",
                    "instructions": f"Task failed: {str(e)}"
                },
                "logs": self._format_logs(),
                "error": str(e)
            }
    
    def _build_reasoning_prompt(self, prompt_context: str, external_tools: Dict[str, Any]) -> str:
        """Build a reasoning prompt optimized for FLAN-T5's capabilities"""
        
        # FLAN-T5 works best with explicit task instructions
        reasoning_prompt = f"""
Answer the following question by reasoning step-by-step. Be thorough and methodical in your analysis.

Question: {prompt_context}

Available tools: {list(external_tools.keys()) if external_tools else "None"}

Please provide a comprehensive response that:
1. Analyzes the question thoroughly
2. Breaks down the problem into logical steps
3. Provides detailed reasoning for each step
4. Gives a clear, well-structured answer
5. Includes actionable insights or recommendations where applicable

Format your response clearly with numbered steps and detailed explanations.
"""
        
        return reasoning_prompt
    
    async def _enhance_with_tools(self, response: str, external_tools: Dict[str, Any]) -> str:
        """Enhance the response using external tools if available"""
        try:
            # For now, we'll use a simple approach to determine if tools should be used
            # In a full implementation, this would be more sophisticated
            
            enhanced_response = response
            
            # Check if we need to use web search
            if "web_search" in external_tools and any(keyword in response.lower() 
                for keyword in ["search", "find", "look up", "research"]):
                search_result = await self._call_external_tool("web_search", external_tools["web_search"], {
                    "query": "relevant information for the task"
                })
                if search_result:
                    enhanced_response += f"\n\nAdditional research findings: {search_result}"
            
            # Check if we need calculator
            if "calculator" in external_tools and any(keyword in response.lower() 
                for keyword in ["calculate", "compute", "math", "number"]):
                calc_result = await self._call_external_tool("calculator", external_tools["calculator"], {
                    "expression": "relevant calculation"
                })
                if calc_result:
                    enhanced_response += f"\n\nCalculation result: {calc_result}"
            
            return enhanced_response
            
        except Exception as e:
            logger.warning("Tool enhancement failed", error=str(e))
            return response
    
    async def _call_external_tool(self, tool_name: str, tool_url: str, parameters: Dict[str, Any]) -> Optional[str]:
        """Call an external tool"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=settings.EXTERNAL_TOOL_TIMEOUT) as client:
                response = await client.post(tool_url, json=parameters)
                response.raise_for_status()
                return f"Tool '{tool_name}' result: {response.text}"
        except Exception as e:
            logger.warning("External tool call failed", tool_name=tool_name, error=str(e))
            return None
    
    async def _generate_reasoning_response(self, prompt: str) -> str:
        """Generate response using FLAN-T5's reasoning capabilities"""
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            
            # Move to device if needed
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate response with FLAN-T5
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=self.max_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                    top_p=self.top_p,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the response
            cleaned_response = self._clean_response(response)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": cleaned_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return cleaned_response
            
        except Exception as e:
            logger.error("FLAN-T5 generation failed", error=str(e))
            raise
    
    async def _generate_final_response(self, enhanced_response: str, original_prompt: str) -> str:
        """Generate the final structured response"""
        
        # Use FLAN-T5 to summarize and structure the final response
        final_prompt = f"""
Summarize and structure the following response into a clear, professional format:

Original question: {original_prompt}

Response: {enhanced_response}

Please provide a well-structured final answer that is:
1. Clear and concise
2. Well-organized with proper formatting
3. Professional in tone
4. Actionable where applicable
5. Easy to understand

Format your response with clear headings and bullet points where appropriate.
"""
        
        return await self._generate_reasoning_response(final_prompt)
    
    def _clean_response(self, text: str) -> str:
        """Clean and format the generated response"""
        # Remove stop sequences
        for stop_seq in self.stop_sequences:
            if stop_seq in text:
                text = text.split(stop_seq)[0]
        
        # Remove extra whitespace
        text = text.strip()
        
        # Remove any remaining prompt artifacts
        if "Response:" in text:
            text = text.split("Response:")[-1].strip()
        
        return text
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not self.tokenizer:
            return 0
        return len(self.tokenizer.encode(text))
    
    def _format_logs(self) -> str:
        """Format execution logs"""
        logs = []
        logs.append(f"Task ID: {self.current_task_id}")
        logs.append(f"Model: {settings.MODEL_NAME} (FLAN-T5 Small)")
        logs.append(f"Model Size: 80M parameters (300MB)")
        logs.append(f"Device: {self.device}")
        logs.append(f"Conversation turns: {len(self.conversation_history)}")
        logs.append(f"Timestamp: {datetime.utcnow().isoformat()}")
        
        return "\n".join(logs)

# Alias for backward compatibility
LlamaAgent = FlanT5Agent