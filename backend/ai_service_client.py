"""
AI Automation Service Client
Handles communication with external AI service for agentic tasks
"""

import requests
import json
import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentConfig:
    """Configuration for AI agent behavior"""
    model: str = "deepseek/deepseek-chat-v3.1:free"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 300  # 5 minutes
    retry_attempts: int = 3

@dataclass
class TaskRequest:
    """Request structure for AI Automation Service"""
    task_id: str
    prompt_context: str
    agent_config: Dict[str, Any]
    external_tool_endpoints: Dict[str, str] = None

@dataclass
class TaskResponse:
    """Response structure from AI Automation Service"""
    task_id: str
    status: str
    agent_reply: str = ""
    next_step: Dict[str, Any] = None
    logs: str = ""
    error: str = None

class AIServiceClient:
    """Client for communicating with AI Automation Service"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or "https://ntbk-ai-flask-api.onrender.com"
        self.api_key = api_key or "notebooker-api-key-2024"
        self.session = requests.Session()
        
        # Set up authentication if API key provided
        if self.api_key:
            self.session.headers.update({
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            })
        else:
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
        
        logger.info(f"🔧 AI Service Client initialized", base_url=self.base_url, has_api_key=bool(self.api_key))
    
    def create_task(self, prompt_context: str, agent_config: AgentConfig = None, 
                   external_tool_endpoints: Dict[str, str] = None) -> str:
        """
        Create a new agentic task and return task_id
        """
        if agent_config is None:
            agent_config = AgentConfig()
        
        task_id = str(uuid.uuid4())
        
        request_data = TaskRequest(
            task_id=task_id,
            prompt_context=prompt_context,
            agent_config=agent_config.__dict__,
            external_tool_endpoints=external_tool_endpoints or {}
        )
        
        try:
            logger.info(f"🚀 Creating AI task", task_id=task_id, base_url=self.base_url)
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/ai/chat",
                json={
                    "message": prompt_context,
                    "projectId": "default",
                    "context": "Engineering notebook assistance"
                },
                timeout=30
            )
            latency = time.time() - start_time
            
            logger.info(f"📡 AI Service API call completed", task_id=task_id, latency=f"{latency:.2f}s", status=response.status_code)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Task created successfully", task_id=task_id)
                return task_id
            else:
                logger.error(f"❌ Failed to create task", status=response.status_code, response=response.text)
                raise Exception(f"AI Service error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Network error creating task", task_id=task_id, error=str(e))
            raise Exception(f"Network error: {e}")
    
    def get_task_status(self, task_id: str) -> TaskResponse:
        """
        Get current status of a task
        """
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/agentic-task/{task_id}",
                timeout=10
            )
            latency = time.time() - start_time
            
            logger.info(f"AI Service status check - Task: {task_id}, Latency: {latency:.2f}s, Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return TaskResponse(
                    task_id=data.get('task_id', task_id),
                    status=data.get('status', 'unknown'),
                    agent_reply=data.get('agent_reply', ''),
                    next_step=data.get('next_step', {}),
                    logs=data.get('logs', ''),
                    error=data.get('error')
                )
            else:
                logger.error(f"Failed to get task status: {response.status_code} - {response.text}")
                return TaskResponse(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    error=f"API error: {response.status_code}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting task status {task_id}: {e}")
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.FAILED.value,
                error=f"Network error: {e}"
            )
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task
        """
        try:
            start_time = time.time()
            response = self.session.delete(
                f"{self.base_url}/agentic-task/{task_id}",
                timeout=10
            )
            latency = time.time() - start_time
            
            logger.info(f"AI Service cancel request - Task: {task_id}, Latency: {latency:.2f}s, Status: {response.status_code}")
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error cancelling task {task_id}: {e}")
            return False
    
    def poll_task_completion(self, task_id: str, max_wait_time: int = 300, 
                           poll_interval: int = 5) -> TaskResponse:
        """
        Poll for task completion with timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = self.get_task_status(task_id)
            
            if response.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                return response
            
            time.sleep(poll_interval)
        
        # Timeout reached
        logger.warning(f"Task {task_id} timed out after {max_wait_time} seconds")
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.FAILED.value,
            error="Task timeout"
        )
    
    def health_check(self) -> bool:
        """
        Check if AI service is available
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

class TaskManager:
    """Manages task lifecycle and state"""
    
    def __init__(self, ai_client: AIServiceClient):
        self.ai_client = ai_client
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
    
    def start_task(self, prompt_context: str, agent_config: AgentConfig = None,
                  external_tool_endpoints: Dict[str, str] = None) -> str:
        """
        Start a new task and track it
        """
        task_id = self.ai_client.create_task(prompt_context, agent_config, external_tool_endpoints)
        
        self.active_tasks[task_id] = {
            'task_id': task_id,
            'status': TaskStatus.PENDING.value,
            'created_at': time.time(),
            'prompt_context': prompt_context,
            'agent_config': agent_config.__dict__ if agent_config else {},
            'external_tool_endpoints': external_tool_endpoints or {}
        }
        
        return task_id
    
    def update_task_status(self, task_id: str) -> TaskResponse:
        """
        Update task status and move to history if completed
        """
        response = self.ai_client.get_task_status(task_id)
        
        if task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = response.status
            self.active_tasks[task_id]['last_updated'] = time.time()
            
            # Move to history if completed
            if response.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                self.active_tasks[task_id]['completed_at'] = time.time()
                self.task_history.append(self.active_tasks[task_id])
                del self.active_tasks[task_id]
        
        return response
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task
        """
        success = self.ai_client.cancel_task(task_id)
        if success and task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = TaskStatus.CANCELLED.value
            self.active_tasks[task_id]['cancelled_at'] = time.time()
        return success
    
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task information
        """
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check history
        for task in self.task_history:
            if task['task_id'] == task_id:
                return task
        
        return None
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all active tasks
        """
        return list(self.active_tasks.values())
    
    def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get task history
        """
        return self.task_history[-limit:]

# Global instances
ai_client = None
task_manager = None

def initialize_ai_service(base_url: str = None, api_key: str = None):
    """Initialize AI service client and task manager"""
    global ai_client, task_manager
    
    ai_client = AIServiceClient(base_url, api_key)
    task_manager = TaskManager(ai_client)
    
    logger.info(f"AI Service initialized with base URL: {ai_client.base_url}")
    
    # Test connection
    if ai_client.health_check():
        logger.info("AI Service health check passed")
    else:
        logger.warning("AI Service health check failed - service may be unavailable")

def get_ai_client() -> AIServiceClient:
    """Get the global AI client instance"""
    if ai_client is None:
        initialize_ai_service()
    return ai_client

def get_task_manager() -> TaskManager:
    """Get the global task manager instance"""
    if task_manager is None:
        initialize_ai_service()
    return task_manager
