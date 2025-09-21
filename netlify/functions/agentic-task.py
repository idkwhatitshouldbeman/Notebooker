"""
Netlify Function for NTBK_AI agentic task endpoint
Simplified implementation for serverless deployment
"""

import json
import os
from datetime import datetime

def handler(event, context):
    """
    Netlify Function handler for agentic tasks
    """
    try:
        # Set CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Content-Type': 'application/json'
        }
        
        # Handle CORS preflight
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Handle health check
        if event['httpMethod'] == 'GET' and event['path'] in ['/api/health', '/health']:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    "status": "healthy",
                    "service": "NTBK_AI Agentic Service",
                    "version": "1.0.0",
                    "platform": "netlify",
                    "timestamp": datetime.utcnow().isoformat()
                })
            }
        
        # Handle agentic task requests
        if event['httpMethod'] == 'POST' and event['path'] == '/api/agentic-task':
            try:
                # Parse request body
                if event.get('body'):
                    request_data = json.loads(event['body'])
                else:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({"error": "No request body provided"})
                    }
                
                # Validate required fields
                if not request_data.get('task_id') or not request_data.get('prompt_context'):
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({"error": "Missing required fields: task_id and prompt_context"})
                    }
                
                # Simulate AI processing (since we can't load the full model in Netlify Functions)
                task_id = request_data['task_id']
                prompt_context = request_data['prompt_context']
                
                # Generate a mock response
                response = {
                    "task_id": task_id,
                    "status": "completed",
                    "agent_reply": f"Mock AI Response: I've analyzed your request about '{prompt_context[:50]}...'. This is a simulated response from the NTBK_AI service running on Netlify Functions. The full FLAN-T5 model would provide detailed analysis here.",
                    "next_step": {
                        "action": "complete",
                        "instructions": "Task completed successfully with mock response"
                    },
                    "logs": f"Task {task_id} processed on Netlify Functions at {datetime.utcnow().isoformat()}",
                    "execution_time": 0.5,
                    "tokens_used": 150,
                    "platform": "netlify"
                }
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(response)
                }
                
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({"error": "Invalid JSON in request body"})
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({"error": f"Processing error: {str(e)}"})
                }
        
        # Handle unknown endpoints
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({"error": "Endpoint not found"})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({"error": f"Internal server error: {str(e)}"})
        }
