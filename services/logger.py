"""
Structured logging configuration for NTBK_AI service
"""

import logging
import sys
from typing import Any, Dict
import structlog
from pythonjsonlogger import jsonlogger

from config.settings import settings

def setup_logging():
    """Setup structured logging with JSON format"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Set up JSON formatter for standard logs
    json_handler = logging.StreamHandler(sys.stdout)
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    json_handler.setFormatter(json_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(json_handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Reduce noise from external libraries
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Create service logger
    service_logger = structlog.get_logger("ntbk_ai")
    service_logger.info("Logging initialized", level=settings.LOG_LEVEL)

class TaskLogger:
    """Specialized logger for task execution tracking"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.logger = structlog.get_logger("task")
        self.logs = []
    
    def log_step(self, step_id: int, action: str, result: str, success: bool = True):
        """Log a task step execution"""
        log_entry = {
            "task_id": self.task_id,
            "step_id": step_id,
            "action": action,
            "result": result[:500],  # Truncate long results
            "success": success,
            "timestamp": structlog.processors.TimeStamper()._make_stamper()()
        }
        
        self.logs.append(log_entry)
        
        if success:
            self.logger.info("Task step completed", **log_entry)
        else:
            self.logger.error("Task step failed", **log_entry)
    
    def log_agent_decision(self, decision: str, reasoning: str = ""):
        """Log agent decision making"""
        log_entry = {
            "task_id": self.task_id,
            "decision": decision,
            "reasoning": reasoning,
            "timestamp": structlog.processors.TimeStamper()._make_stamper()()
        }
        
        self.logs.append(log_entry)
        self.logger.info("Agent decision", **log_entry)
    
    def log_tool_call(self, tool_name: str, parameters: Dict[str, Any], result: str, success: bool = True):
        """Log external tool calls"""
        log_entry = {
            "task_id": self.task_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result[:500],  # Truncate long results
            "success": success,
            "timestamp": structlog.processors.TimeStamper()._make_stamper()()
        }
        
        self.logs.append(log_entry)
        
        if success:
            self.logger.info("Tool call completed", **log_entry)
        else:
            self.logger.error("Tool call failed", **log_entry)
    
    def log_error(self, error: str, context: Dict[str, Any] = None):
        """Log task errors"""
        log_entry = {
            "task_id": self.task_id,
            "error": error,
            "context": context or {},
            "timestamp": structlog.processors.TimeStamper()._make_stamper()()
        }
        
        self.logs.append(log_entry)
        self.logger.error("Task error", **log_entry)
    
    def get_logs(self) -> str:
        """Get formatted logs as string"""
        return "\n".join([
            f"[{log['timestamp']}] {log.get('action', 'LOG')}: {log.get('result', log.get('error', ''))}"
            for log in self.logs
        ])
    
    def get_structured_logs(self) -> list:
        """Get logs as structured data"""
        return self.logs
