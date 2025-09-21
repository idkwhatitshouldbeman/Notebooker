"""
AI Service Configuration
Configuration settings for the AI Automation Service integration
"""

import os
from typing import Dict, Any

# AI Service Configuration
AI_SERVICE_CONFIG = {
    # Default AI service URL (can be overridden by environment variable)
    'base_url': os.environ.get('AI_SERVICE_URL', 'https://your-render-app-name.onrender.com'),
    
    # API Key for authentication (optional)
    'api_key': os.environ.get('AI_API_KEY'),
    
    # Default model configuration
    'default_model': 'flan-t5-small',
    
    # Available models
    'available_models': [
        'flan-t5-small',
        'flan-t5-base',
        'flan-t5-large'
    ],
    
    # Task configuration
    'task_config': {
        'default_timeout': 300,  # 5 minutes
        'default_retry_attempts': 3,
        'poll_interval': 5,  # seconds
        'max_wait_time': 300  # 5 minutes
    },
    
    # Model-specific configurations
    'model_configs': {
        'flan-t5-small': {
            'temperature': 0.7,
            'max_tokens': 1000,
            'timeout': 300,
            'top_p': 0.9,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        },
        'flan-t5-base': {
            'temperature': 0.7,
            'max_tokens': 1500,
            'timeout': 300,
            'top_p': 0.9,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        },
        'flan-t5-large': {
            'temperature': 0.7,
            'max_tokens': 2000,
            'timeout': 300,
            'top_p': 0.9,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        }
    }
}

def get_ai_config() -> Dict[str, Any]:
    """Get AI service configuration"""
    return AI_SERVICE_CONFIG

def get_model_config(model_name: str) -> Dict[str, Any]:
    """Get configuration for a specific model"""
    return AI_SERVICE_CONFIG['model_configs'].get(model_name, AI_SERVICE_CONFIG['model_configs']['deepseek/deepseek-chat-v3.1:free'])

def get_available_models() -> list:
    """Get list of available models"""
    return AI_SERVICE_CONFIG['available_models']

def is_ai_service_configured() -> bool:
    """Check if AI service is properly configured"""
    return bool(AI_SERVICE_CONFIG['base_url'])

def get_ai_service_url() -> str:
    """Get AI service URL"""
    return AI_SERVICE_CONFIG['base_url']

def get_ai_api_key() -> str:
    """Get AI service API key"""
    return AI_SERVICE_CONFIG['api_key']
