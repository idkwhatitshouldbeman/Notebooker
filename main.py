"""
NTBK_AI - Independent AI Agentic Automation Microservice
Powered by Llama 3.2 1B model for autonomous multi-step workflows
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from models.llama_agent import LlamaAgent
from services.task_manager import TaskManager
from services.security import SecurityValidator
from services.logger import setup_logging
from config.settings import Settings

# Initialize settings and logging
settings = Settings()
setup_logging()
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="NTBK_AI Agentic Service",
    description="Independent AI agentic automation microservice with Llama 3.2 1B",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
task_manager = TaskManager()
security_validator = SecurityValidator()
llama_agent = LlamaAgent()

# Pydantic models for API
class AgentConfig(BaseModel):
    """Configuration for the agent model"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    stop_sequences: List[str] = Field(default_factory=list)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)

class ExternalToolEndpoints(BaseModel):
    """External tool endpoint configuration"""
    web_search: Optional[str] = None
    calculator: Optional[str] = None
    database_query: Optional[str] = None
    custom_tools: Dict[str, str] = Field(default_factory=dict)

class AgenticTaskRequest(BaseModel):
    """Request model for agentic task submission"""
    task_id: str = Field(..., min_length=1, max_length=100)
    prompt_context: str = Field(..., min_length=1, max_length=10000)
    agent_config: AgentConfig = Field(default_factory=AgentConfig)
    external_tool_endpoints: ExternalToolEndpoints = Field(default_factory=ExternalToolEndpoints)
    
    @validator('task_id')
    def validate_task_id(cls, v):
        if not security_validator.is_safe_string(v):
            raise ValueError("Invalid task_id format")
        return v
    
    @validator('prompt_context')
    def validate_prompt_context(cls, v):
        if not security_validator.is_safe_string(v):
            raise ValueError("Invalid prompt_context format")
        return v

class NextStep(BaseModel):
    """Next step instructions for the client"""
    action: str = Field(..., regex="^(continue|complete|wait_for_tool|retry)$")
    instructions: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    estimated_duration: Optional[int] = None  # seconds

class AgenticTaskResponse(BaseModel):
    """Response model for agentic task processing"""
    task_id: str
    status: str = Field(..., regex="^(in_progress|completed|failed)$")
    agent_reply: str
    next_step: NextStep
    logs: str
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "NTBK_AI Agentic Service",
        "version": "1.0.0"
    }

# Main agentic task endpoint
@app.post("/agentic-task", response_model=AgenticTaskResponse)
async def process_agentic_task(
    request: AgenticTaskRequest,
    background_tasks: BackgroundTasks
) -> AgenticTaskResponse:
    """
    Process an agentic task with autonomous multi-step workflows
    """
    start_time = time.time()
    task_id = request.task_id
    
    try:
        logger.info("Processing agentic task", task_id=task_id)
        
        # Validate and sanitize inputs
        security_validator.validate_request(request)
        
        # Check if task already exists
        existing_task = await task_manager.get_task(task_id)
        if existing_task:
            logger.info("Resuming existing task", task_id=task_id)
            return await _resume_task(existing_task, request)
        
        # Create new task
        task_context = {
            "task_id": task_id,
            "prompt_context": request.prompt_context,
            "agent_config": request.agent_config.dict(),
            "external_tool_endpoints": request.external_tool_endpoints.dict(),
            "created_at": datetime.utcnow().isoformat(),
            "status": "in_progress",
            "steps_completed": 0,
            "conversation_history": []
        }
        
        await task_manager.create_task(task_id, task_context)
        
        # Process the task with the agent
        result = await _process_task_with_agent(request, task_context)
        
        execution_time = time.time() - start_time
        
        # Update task status
        task_context.update({
            "status": result["status"],
            "last_updated": datetime.utcnow().isoformat(),
            "execution_time": execution_time
        })
        await task_manager.update_task(task_id, task_context)
        
        logger.info("Task processing completed", 
                   task_id=task_id, 
                   status=result["status"],
                   execution_time=execution_time)
        
        return AgenticTaskResponse(
            task_id=task_id,
            status=result["status"],
            agent_reply=result["agent_reply"],
            next_step=result["next_step"],
            logs=result["logs"],
            error=result.get("error"),
            execution_time=execution_time,
            tokens_used=result.get("tokens_used")
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Task processing failed: {str(e)}"
        logger.error("Task processing error", 
                    task_id=task_id, 
                    error=error_msg,
                    execution_time=execution_time)
        
        # Update task with error status
        try:
            await task_manager.update_task(task_id, {
                "status": "failed",
                "error": error_msg,
                "last_updated": datetime.utcnow().isoformat(),
                "execution_time": execution_time
            })
        except:
            pass  # Don't fail on cleanup errors
        
        return AgenticTaskResponse(
            task_id=task_id,
            status="failed",
            agent_reply="",
            next_step=NextStep(
                action="retry",
                instructions="Task failed due to internal error. Please retry with a new task_id."
            ),
            logs=f"Error: {error_msg}",
            error=error_msg,
            execution_time=execution_time
        )

async def _process_task_with_agent(request: AgenticTaskRequest, task_context: Dict[str, Any]) -> Dict[str, Any]:
    """Process the task using the Llama agent"""
    try:
        # Configure the agent
        llama_agent.configure(
            temperature=request.agent_config.temperature,
            max_tokens=request.agent_config.max_tokens,
            stop_sequences=request.agent_config.stop_sequences,
            top_p=request.agent_config.top_p,
            frequency_penalty=request.agent_config.frequency_penalty,
            presence_penalty=request.agent_config.presence_penalty
        )
        
        # Process the task
        result = await llama_agent.process_task(
            prompt_context=request.prompt_context,
            task_context=task_context,
            external_tools=request.external_tool_endpoints.dict()
        )
        
        return result
        
    except Exception as e:
        logger.error("Agent processing error", error=str(e))
        return {
            "status": "failed",
            "agent_reply": "",
            "next_step": NextStep(
                action="retry",
                instructions="Agent processing failed. Please retry."
            ),
            "logs": f"Agent error: {str(e)}",
            "error": str(e)
        }

async def _resume_task(existing_task: Dict[str, Any], request: AgenticTaskRequest) -> AgenticTaskResponse:
    """Resume an existing task"""
    # For now, return the existing task status
    # In a full implementation, this would handle task resumption logic
    return AgenticTaskResponse(
        task_id=existing_task["task_id"],
        status=existing_task["status"],
        agent_reply=existing_task.get("agent_reply", ""),
        next_step=NextStep(
            action="continue" if existing_task["status"] == "in_progress" else "complete",
            instructions="Task resumed from previous state"
        ),
        logs=existing_task.get("logs", ""),
        error=existing_task.get("error")
    )

# Task management endpoints
@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a specific task"""
    try:
        task = await task_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        logger.error("Error retrieving task", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    try:
        success = await task_manager.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task cancelled successfully"}
    except Exception as e:
        logger.error("Error cancelling task", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
