# 🚨 URGENT: Fix CORS Issue in Render AI Service

## Problem
The frontend is getting CORS errors when trying to connect to the AI service:
```
Access to XMLHttpRequest at 'https://ntbk-ai-flask-api.onrender.com/api/ai/chat' from origin 'https://notebooker.netlify.app' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution Required

### 1. Add CORS Support to Flask App
Add this to your Flask app (app.py):

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "https://notebooker.netlify.app",
    "http://localhost:8080",
    "http://localhost:3000"
])
```

### 2. Add Health Endpoint
Add this endpoint to wake up the service:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy", "service": "ntbk-ai-flask-api"}, 200
```

### 3. Update requirements.txt
Make sure you have:
```
flask-cors==4.0.0
```

### 4. Test CORS
After deploying, test with:
```bash
curl -H "Origin: https://notebooker.netlify.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-API-Key" \
     -X OPTIONS \
     https://ntbk-ai-flask-api.onrender.com/api/ai/chat
```

## Expected Response
Should return CORS headers:
```
Access-Control-Allow-Origin: https://notebooker.netlify.app
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: X-API-Key, Content-Type
```

## Priority: HIGH
This is blocking all AI functionality in the frontend!
