"""
Netlify Function wrapper for the NTBK_AI agentic task endpoint
"""

import json
import sys
import os
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from main import app
    from fastapi import Request
    import asyncio
    from fastapi.responses import JSONResponse
except ImportError as e:
    print(f"Import error: {e}")
    app = None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests to /api/agentic-task"""
        if not app:
            self.send_error(500, "FastAPI app not available")
            return
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Create FastAPI request object
            scope = {
                "type": "http",
                "method": "POST",
                "path": "/agentic-task",
                "headers": [(k.lower().encode(), v.encode()) for k, v in self.headers.items()],
                "query_string": b"",
                "client": ("127.0.0.1", 0),
                "server": ("127.0.0.1", 0),
            }
            
            # Create a simple request object
            class SimpleRequest:
                def __init__(self, scope, body):
                    self.scope = scope
                    self._body = body
                    self.method = scope["method"]
                    self.url = f"http://localhost{scope['path']}"
                    self.headers = {k.decode(): v.decode() for k, v in scope["headers"]}
                
                async def json(self):
                    return request_data
            
            request = SimpleRequest(scope, post_data)
            
            # Call the FastAPI endpoint
            async def process_request():
                from main import process_agentic_task
                from main import AgenticTaskRequest
                
                # Create the request model
                agentic_request = AgenticTaskRequest(**request_data)
                
                # Process the request
                result = await process_agentic_task(agentic_request, None)
                
                return result
            
            # Run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response_data = loop.run_until_complete(process_request())
            finally:
                loop.close()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_json = json.dumps(response_data.dict() if hasattr(response_data, 'dict') else response_data)
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests (health check)"""
        if self.path == "/api/health" or self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            health_response = {
                "status": "healthy",
                "service": "NTBK_AI Agentic Service",
                "version": "1.0.0",
                "platform": "netlify"
            }
            
            self.wfile.write(json.dumps(health_response).encode('utf-8'))
        else:
            self.send_error(404, "Not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_header()
