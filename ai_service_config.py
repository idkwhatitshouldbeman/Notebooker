"""
AI Service Configuration
Configuration settings for the AI Automation Service integration
"""

import os
from typing import Dict, Any

# AI Service Configuration
AI_SERVICE_CONFIG = {
    # Default AI service URL (can be overridden by environment variable)
    'base_url': os.environ.get('AI_SERVICE_URL', 'https://n8n-workflow-automation.onrender.com'),
    
    # API Key for authentication (optional)
    'api_key': os.environ.get('AI_API_KEY'),
    
    # Default model configuration
    'default_model': 'deepseek/deepseek-chat-v3.1:free',
    
    # Available models
    'available_models': [
        'deepseek/deepseek-chat-v3.1:free',
        'gpt-oss-20b:free',
        'sonoma-dusk-alpha:free',
        'kimi-k2:free',
        'gemma-3n-2b:free',
        'mistral-small-3.2-24b:free'
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
        'deepseek/deepseek-chat-v3.1:free': {
            'temperature': 0.7,
            'max_tokens': 2000,
            'timeout': 300
        },
        'gpt-oss-20b:free': {
            'temperature': 0.7,
            'max_tokens': 1500,
            'timeout': 300
        },
        'sonoma-dusk-alpha:free': {
            'temperature': 0.6,
            'max_tokens': 1800,
            'timeout': 300
        },
        'kimi-k2:free': {
            'temperature': 0.7,
            'max_tokens': 2000,
            'timeout': 300
        },
        'gemma-3n-2b:free': {
            'temperature': 0.8,
            'max_tokens': 1200,
            'timeout': 300
        },
        'mistral-small-3.2-24b:free': {
            'temperature': 0.7,
            'max_tokens': 1600,
            'timeout': 300
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
