"""
Task Manager for Stateful Task Context Management
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from config.settings import settings

logger = structlog.get_logger()

class TaskManager:
    """
    Manages stateful task context with Redis backend and in-memory fallback
    """
    
    def __init__(self):
        self.redis_client = None
        self.in_memory_tasks = {}  # Fallback storage
        self.task_timeouts = {}
        self.is_redis_connected = False
        
    async def initialize(self):
        """Initialize the task manager with Redis connection"""
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                
                # Test connection
                await self.redis_client.ping()
                self.is_redis_connected = True
                logger.info("Task manager initialized with Redis")
                
            except Exception as e:
                logger.warning("Redis connection failed, using in-memory storage", error=str(e))
                self.is_redis_connected = False
        else:
            logger.warning("Redis not available, using in-memory storage")
            self.is_redis_connected = False
    
    async def create_task(self, task_id: str, task_context: Dict[str, Any]) -> bool:
        """Create a new task with initial context"""
        try:
            task_context.update({
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "status": "in_progress"
            })
            
            if self.is_redis_connected:
                await self.redis_client.setex(
                    f"task:{task_id}",
                    settings.TASK_TIMEOUT,
                    json.dumps(task_context)
                )
            else:
                self.in_memory_tasks[task_id] = task_context
                # Set cleanup timer
                self.task_timeouts[task_id] = time.time() + settings.TASK_TIMEOUT
            
            logger.info("Task created", task_id=task_id)
            return True
            
        except Exception as e:
            logger.error("Failed to create task", task_id=task_id, error=str(e))
            return False
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task by ID"""
        try:
            if self.is_redis_connected:
                task_data = await self.redis_client.get(f"task:{task_id}")
                if task_data:
                    return json.loads(task_data)
            else:
                # Check if task exists and hasn't expired
                if task_id in self.in_memory_tasks:
                    if time.time() < self.task_timeouts.get(task_id, 0):
                        return self.in_memory_tasks[task_id]
                    else:
                        # Task expired, clean up
                        await self._cleanup_task(task_id)
            
            return None
            
        except Exception as e:
            logger.error("Failed to retrieve task", task_id=task_id, error=str(e))
            return None
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing task"""
        try:
            # Get current task
            current_task = await self.get_task(task_id)
            if not current_task:
                logger.warning("Task not found for update", task_id=task_id)
                return False
            
            # Merge updates
            current_task.update(updates)
            current_task["last_updated"] = datetime.utcnow().isoformat()
            
            if self.is_redis_connected:
                await self.redis_client.setex(
                    f"task:{task_id}",
                    settings.TASK_TIMEOUT,
                    json.dumps(current_task)
                )
            else:
                self.in_memory_tasks[task_id] = current_task
                # Reset timeout
                self.task_timeouts[task_id] = time.time() + settings.TASK_TIMEOUT
            
            logger.info("Task updated", task_id=task_id)
            return True
            
        except Exception as e:
            logger.error("Failed to update task", task_id=task_id, error=str(e))
            return False
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        try:
            task = await self.get_task(task_id)
            if not task:
                return False
            
            # Update status to cancelled
            await self.update_task(task_id, {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow().isoformat()
            })
            
            logger.info("Task cancelled", task_id=task_id)
            return True
            
        except Exception as e:
            logger.error("Failed to cancel task", task_id=task_id, error=str(e))
            return False
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task completely"""
        try:
            if self.is_redis_connected:
                await self.redis_client.delete(f"task:{task_id}")
            else:
                if task_id in self.in_memory_tasks:
                    del self.in_memory_tasks[task_id]
                if task_id in self.task_timeouts:
                    del self.task_timeouts[task_id]
            
            logger.info("Task deleted", task_id=task_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete task", task_id=task_id, error=str(e))
            return False
    
    async def list_tasks(self, status_filter: Optional[str] = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """List tasks with optional status filter"""
        try:
            tasks = []
            
            if self.is_redis_connected:
                # Get all task keys
                task_keys = await self.redis_client.keys("task:*")
                
                for key in task_keys[:limit]:
                    task_data = await self.redis_client.get(key)
                    if task_data:
                        task = json.loads(task_data)
                        if not status_filter or task.get("status") == status_filter:
                            tasks.append(task)
            else:
                # In-memory fallback
                for task_id, task in self.in_memory_tasks.items():
                    if time.time() < self.task_timeouts.get(task_id, 0):
                        if not status_filter or task.get("status") == status_filter:
                            tasks.append(task)
                    else:
                        # Clean up expired task
                        await self._cleanup_task(task_id)
            
            # Sort by creation time (newest first)
            tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return tasks[:limit]
            
        except Exception as e:
            logger.error("Failed to list tasks", error=str(e))
            return []
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        try:
            all_tasks = await self.list_tasks()
            
            stats = {
                "total_tasks": len(all_tasks),
                "status_counts": {},
                "average_execution_time": 0,
                "oldest_task": None,
                "newest_task": None
            }
            
            execution_times = []
            
            for task in all_tasks:
                status = task.get("status", "unknown")
                stats["status_counts"][status] = stats["status_counts"].get(status, 0) + 1
                
                if task.get("execution_time"):
                    execution_times.append(task["execution_time"])
                
                created_at = task.get("created_at")
                if created_at:
                    if not stats["oldest_task"] or created_at < stats["oldest_task"]:
                        stats["oldest_task"] = created_at
                    if not stats["newest_task"] or created_at > stats["newest_task"]:
                        stats["newest_task"] = created_at
            
            if execution_times:
                stats["average_execution_time"] = sum(execution_times) / len(execution_times)
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get task statistics", error=str(e))
            return {}
    
    async def cleanup_expired_tasks(self):
        """Clean up expired tasks"""
        try:
            if self.is_redis_connected:
                # Redis handles expiration automatically
                return
            
            # Clean up in-memory expired tasks
            current_time = time.time()
            expired_tasks = []
            
            for task_id, timeout in self.task_timeouts.items():
                if current_time >= timeout:
                    expired_tasks.append(task_id)
            
            for task_id in expired_tasks:
                await self._cleanup_task(task_id)
            
            if expired_tasks:
                logger.info("Cleaned up expired tasks", count=len(expired_tasks))
                
        except Exception as e:
            logger.error("Failed to cleanup expired tasks", error=str(e))
    
    async def _cleanup_task(self, task_id: str):
        """Clean up a specific task"""
        try:
            if task_id in self.in_memory_tasks:
                del self.in_memory_tasks[task_id]
            if task_id in self.task_timeouts:
                del self.task_timeouts[task_id]
        except Exception as e:
            logger.error("Failed to cleanup task", task_id=task_id, error=str(e))
    
    async def start_cleanup_scheduler(self):
        """Start the cleanup scheduler"""
        while True:
            try:
                await asyncio.sleep(settings.TASK_CLEANUP_INTERVAL)
                await self.cleanup_expired_tasks()
            except Exception as e:
                logger.error("Cleanup scheduler error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying
    
    async def close(self):
        """Close the task manager and cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Task manager closed")
        except Exception as e:
            logger.error("Error closing task manager", error=str(e))
