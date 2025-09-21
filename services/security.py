"""
Security validation and input sanitization
"""

import re
import html
import json
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger()

class SecurityValidator:
    """Input validation and security measures"""
    
    def __init__(self):
        # Dangerous patterns to block
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'import\s+os',
            r'subprocess',
            r'shell\s*=\s*True',
            r'rm\s+-rf',
            r'del\s+/f',
            r'format\s+c:',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
        
        # Allowed characters for safe strings
        self.safe_char_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.,!?@#$%^&*()+=\[\]{}|\\:";\'<>/`~]*$')
    
    def is_safe_string(self, text: str) -> bool:
        """Check if a string is safe (no dangerous patterns)"""
        if not isinstance(text, str):
            return False
        
        # Check length
        if len(text) > 10000:  # Max 10KB
            return False
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                logger.warning("Dangerous pattern detected", pattern=pattern.pattern)
                return False
        
        return True
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize a string by removing dangerous content"""
        if not isinstance(text, str):
            return ""
        
        # HTML escape
        text = html.escape(text)
        
        # Remove dangerous patterns
        for pattern in self.compiled_patterns:
            text = pattern.sub('', text)
        
        # Limit length
        if len(text) > 10000:
            text = text[:10000]
        
        return text.strip()
    
    def validate_request(self, request_data: Any) -> bool:
        """Validate a complete request object"""
        try:
            # Convert to dict if it's a Pydantic model
            if hasattr(request_data, 'dict'):
                data = request_data.dict()
            else:
                data = request_data
            
            # Validate task_id
            if 'task_id' in data:
                if not self.is_safe_string(str(data['task_id'])):
                    raise ValueError("Invalid task_id")
            
            # Validate prompt_context
            if 'prompt_context' in data:
                if not self.is_safe_string(str(data['prompt_context'])):
                    raise ValueError("Invalid prompt_context")
            
            # Validate agent_config
            if 'agent_config' in data:
                self._validate_agent_config(data['agent_config'])
            
            # Validate external_tool_endpoints
            if 'external_tool_endpoints' in data:
                self._validate_tool_endpoints(data['external_tool_endpoints'])
            
            return True
            
        except Exception as e:
            logger.error("Request validation failed", error=str(e))
            raise
    
    def _validate_agent_config(self, config: Dict[str, Any]) -> bool:
        """Validate agent configuration"""
        # Check temperature
        if 'temperature' in config:
            temp = config['temperature']
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                raise ValueError("Invalid temperature value")
        
        # Check max_tokens
        if 'max_tokens' in config:
            tokens = config['max_tokens']
            if not isinstance(tokens, int) or tokens < 1 or tokens > 4000:
                raise ValueError("Invalid max_tokens value")
        
        # Check stop_sequences
        if 'stop_sequences' in config:
            sequences = config['stop_sequences']
            if not isinstance(sequences, list):
                raise ValueError("stop_sequences must be a list")
            for seq in sequences:
                if not self.is_safe_string(str(seq)):
                    raise ValueError("Invalid stop sequence")
        
        return True
    
    def _validate_tool_endpoints(self, endpoints: Dict[str, Any]) -> bool:
        """Validate external tool endpoints"""
        for key, value in endpoints.items():
            if not self.is_safe_string(str(key)):
                raise ValueError(f"Invalid tool key: {key}")
            
            if value is not None:
                if not self.is_safe_string(str(value)):
                    raise ValueError(f"Invalid tool endpoint: {value}")
                
                # Basic URL validation
                if not self._is_valid_url(str(value)):
                    raise ValueError(f"Invalid URL format: {value}")
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def validate_json_input(self, json_str: str) -> Dict[str, Any]:
        """Validate and parse JSON input"""
        try:
            # Check if it's safe
            if not self.is_safe_string(json_str):
                raise ValueError("Unsafe JSON content")
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate structure
            if not isinstance(data, dict):
                raise ValueError("JSON must be an object")
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"JSON validation failed: {str(e)}")
    
    def sanitize_tool_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize tool parameters"""
        sanitized = {}
        
        for key, value in params.items():
            # Sanitize key
            safe_key = self.sanitize_string(str(key))
            if not safe_key:
                continue
            
            # Sanitize value based on type
            if isinstance(value, str):
                safe_value = self.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                safe_value = value
            elif isinstance(value, list):
                safe_value = [self.sanitize_string(str(item)) if isinstance(item, str) else item 
                             for item in value]
            elif isinstance(value, dict):
                safe_value = self.sanitize_tool_parameters(value)
            else:
                safe_value = self.sanitize_string(str(value))
            
            sanitized[safe_key] = safe_value
        
        return sanitized
