"""
Netlify Function for health check endpoint
"""

import json
from datetime import datetime

def handler(event, context):
    """
    Health check endpoint for Netlify Functions
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Return health status
    health_data = {
        "status": "healthy",
        "service": "NTBK_AI Agentic Service",
        "version": "1.0.0",
        "platform": "netlify",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "agentic_task": "/api/agentic-task",
            "health": "/api/health"
        }
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(health_data)
    }
