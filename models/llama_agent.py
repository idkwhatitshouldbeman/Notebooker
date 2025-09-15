"""
Llama 3.2 1B Agent Implementation for Autonomous Workflows
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
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = structlog.get_logger()

class LlamaAgent:
    """
    Autonomous agent powered by Llama 3.2 1B for multi-step workflows
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
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
        """Initialize the Llama model and tokenizer"""
        if self.is_initialized:
            return
            
        try:
            logger.info("Initializing Llama 3.2 1B model", device=self.device)
            
            # Configure quantization for memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR,
                quantization_config=quantization_config if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self.is_initialized = True
            logger.info("Llama model initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Llama model", error=str(e))
            raise
    
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
        Process an agentic task with autonomous multi-step workflows
        """
        if not self.is_initialized:
            await self.initialize()
        
        self.current_task_id = task_context.get("task_id")
        self.conversation_history = task_context.get("conversation_history", [])
        
        try:
            logger.info("Starting agentic task processing", task_id=self.current_task_id)
            
            # Analyze the task and create a plan
            task_plan = await self._analyze_task(prompt_context, external_tools)
            
            # Execute the plan step by step
            results = await self._execute_plan(task_plan, external_tools)
            
            # Generate final response
            final_response = await self._generate_final_response(results)
            
            return {
                "status": "completed",
                "agent_reply": final_response,
                "next_step": {
                    "action": "complete",
                    "instructions": "Task completed successfully"
                },
                "logs": self._format_logs(),
                "tokens_used": self._count_tokens(prompt_context + final_response)
            }
            
        except Exception as e:
            logger.error("Task processing failed", task_id=self.current_task_id, error=str(e))
            return {
                "status": "failed",
                "agent_reply": "",
                "next_step": {
                    "action": "retry",
                    "instructions": f"Task failed: {str(e)}"
                },
                "logs": self._format_logs(),
                "error": str(e)
            }
    
    async def _analyze_task(self, prompt_context: str, external_tools: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the task and create an execution plan"""
        
        analysis_prompt = f"""
You are an autonomous AI agent. Analyze the following task and create a step-by-step execution plan.

Task: {prompt_context}

Available tools: {list(external_tools.keys()) if external_tools else "None"}

Create a JSON plan with the following structure:
{{
    "objective": "Clear description of what needs to be accomplished",
    "steps": [
        {{
            "step_id": 1,
            "action": "reasoning|tool_call|writing|research",
            "description": "What this step will do",
            "tool": "tool_name_if_applicable",
            "parameters": {{"param": "value"}},
            "expected_output": "What we expect from this step"
        }}
    ],
    "estimated_completion": "How long this might take"
}}

Respond with only the JSON plan, no additional text.
"""
        
        plan_response = await self._generate_text(analysis_prompt)
        
        try:
            # Extract JSON from response
            json_start = plan_response.find('{')
            json_end = plan_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                plan_json = plan_response[json_start:json_end]
                plan = json.loads(plan_json)
            else:
                # Fallback plan if JSON parsing fails
                plan = {
                    "objective": "Complete the given task",
                    "steps": [
                        {
                            "step_id": 1,
                            "action": "reasoning",
                            "description": "Analyze and process the task",
                            "expected_output": "Understanding and solution"
                        }
                    ],
                    "estimated_completion": "Unknown"
                }
        except json.JSONDecodeError:
            # Fallback plan
            plan = {
                "objective": "Complete the given task",
                "steps": [
                    {
                        "step_id": 1,
                        "action": "reasoning",
                        "description": "Analyze and process the task",
                        "expected_output": "Understanding and solution"
                    }
                ],
                "estimated_completion": "Unknown"
            }
        
        logger.info("Task analysis completed", 
                   task_id=self.current_task_id,
                   steps_count=len(plan.get("steps", [])))
        
        return plan
    
    async def _execute_plan(self, plan: Dict[str, Any], external_tools: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the task plan step by step"""
        results = []
        steps = plan.get("steps", [])
        
        for step in steps:
            try:
                logger.info("Executing step", 
                           task_id=self.current_task_id,
                           step_id=step.get("step_id"),
                           action=step.get("action"))
                
                if step.get("action") == "tool_call":
                    result = await self._execute_tool_call(step, external_tools)
                elif step.get("action") == "reasoning":
                    result = await self._execute_reasoning(step)
                elif step.get("action") == "writing":
                    result = await self._execute_writing(step)
                elif step.get("action") == "research":
                    result = await self._execute_research(step, external_tools)
                else:
                    result = await self._execute_generic_step(step)
                
                results.append({
                    "step_id": step.get("step_id"),
                    "action": step.get("action"),
                    "result": result,
                    "success": True,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"Step {step.get('step_id')}: {result}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.error("Step execution failed",
                           task_id=self.current_task_id,
                           step_id=step.get("step_id"),
                           error=str(e))
                
                results.append({
                    "step_id": step.get("step_id"),
                    "action": step.get("action"),
                    "result": f"Error: {str(e)}",
                    "success": False,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return results
    
    async def _execute_tool_call(self, step: Dict[str, Any], external_tools: Dict[str, Any]) -> str:
        """Execute an external tool call"""
        tool_name = step.get("tool")
        parameters = step.get("parameters", {})
        
        if tool_name not in external_tools:
            return f"Tool '{tool_name}' not available"
        
        tool_url = external_tools[tool_name]
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=settings.EXTERNAL_TOOL_TIMEOUT) as client:
                response = await client.post(tool_url, json=parameters)
                response.raise_for_status()
                return f"Tool '{tool_name}' result: {response.text}"
        except Exception as e:
            return f"Tool '{tool_name}' failed: {str(e)}"
    
    async def _execute_reasoning(self, step: Dict[str, Any]) -> str:
        """Execute reasoning step"""
        reasoning_prompt = f"""
You are an AI agent performing reasoning. 

Task: {step.get('description', '')}
Expected output: {step.get('expected_output', '')}

Provide clear, logical reasoning and analysis. Be thorough and methodical.
"""
        
        return await self._generate_text(reasoning_prompt)
    
    async def _execute_writing(self, step: Dict[str, Any]) -> str:
        """Execute writing step"""
        writing_prompt = f"""
You are an AI agent performing writing tasks.

Task: {step.get('description', '')}
Expected output: {step.get('expected_output', '')}

Write high-quality, well-structured content. Be clear, concise, and engaging.
"""
        
        return await self._generate_text(writing_prompt)
    
    async def _execute_research(self, step: Dict[str, Any], external_tools: Dict[str, Any]) -> str:
        """Execute research step"""
        # For now, use reasoning as research fallback
        # In a full implementation, this would use web search tools
        return await self._execute_reasoning(step)
    
    async def _execute_generic_step(self, step: Dict[str, Any]) -> str:
        """Execute a generic step"""
        generic_prompt = f"""
You are an AI agent performing a task step.

Task: {step.get('description', '')}
Expected output: {step.get('expected_output', '')}

Complete this step effectively and provide the expected output.
"""
        
        return await self._generate_text(generic_prompt)
    
    async def _generate_final_response(self, results: List[Dict[str, Any]]) -> str:
        """Generate the final response based on all step results"""
        
        # Summarize all results
        results_summary = "\n".join([
            f"Step {r['step_id']} ({r['action']}): {r['result'][:200]}..."
            for r in results
        ])
        
        final_prompt = f"""
You are an AI agent providing a final response to a completed task.

Task results summary:
{results_summary}

Provide a comprehensive, well-structured final response that:
1. Summarizes what was accomplished
2. Highlights key findings or results
3. Provides actionable insights or recommendations
4. Is clear and professional

Format your response appropriately for the task type.
"""
        
        return await self._generate_text(final_prompt)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_text(self, prompt: str) -> str:
        """Generate text using the Llama model"""
        try:
            # Prepare the prompt with conversation history
            full_prompt = self._build_conversation_prompt(prompt)
            
            # Generate response
            response = self.pipeline(
                full_prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )
            
            generated_text = response[0]['generated_text']
            
            # Clean up the response
            cleaned_text = self._clean_response(generated_text)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": cleaned_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return cleaned_text
            
        except Exception as e:
            logger.error("Text generation failed", error=str(e))
            raise
    
    def _build_conversation_prompt(self, current_prompt: str) -> str:
        """Build a prompt with conversation history"""
        if not self.conversation_history:
            return current_prompt
        
        # Build conversation context
        context = "Previous conversation:\n"
        for msg in self.conversation_history[-10:]:  # Last 10 messages
            role = "Human" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        context += f"\nCurrent request:\n{current_prompt}\n\nAssistant:"
        return context
    
    def _clean_response(self, text: str) -> str:
        """Clean and format the generated response"""
        # Remove stop sequences
        for stop_seq in self.stop_sequences:
            if stop_seq in text:
                text = text.split(stop_seq)[0]
        
        # Remove extra whitespace
        text = text.strip()
        
        # Remove any remaining prompt artifacts
        if "Assistant:" in text:
            text = text.split("Assistant:")[-1].strip()
        
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
        logs.append(f"Model: {settings.MODEL_NAME}")
        logs.append(f"Device: {self.device}")
        logs.append(f"Conversation turns: {len(self.conversation_history)}")
        logs.append(f"Timestamp: {datetime.utcnow().isoformat()}")
        
        return "\n".join(logs)
