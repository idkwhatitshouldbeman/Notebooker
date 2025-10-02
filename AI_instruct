# NTBK_AI API Deployment Guide

## 🚀 Quick Deployment to Render

### 1. Deploy Flask API to Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**: `idkwhatitshouldbeman/NTBK_AI`
4. **Configure the service:**
   - **Name**: `ntbk-ai-flask-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: `Starter` (free tier)

### 2. Set Environment Variables

In Render dashboard, go to your service → Environment tab:

```env
API_KEY=notebooker-api-key-2024
SECRET_KEY=your-secret-key-change-in-production
AI_SERVICE_URL=https://your-ai-service.onrender.com
PORT=5002
DEBUG=false
LOG_LEVEL=INFO
```

### 3. Deploy

Click **"Deploy"** and wait for the build to complete.

## 📋 API Endpoints

Your Flask API will be available at: `https://ntbk-ai-flask-api.onrender.com`

### Available Endpoints:

#### POST `/api/ai/chat`
```json
{
  "message": "Help me with my project",
  "projectId": "project-123",
  "context": "Robotics project"
}
```

#### POST `/api/ai/analyze`
```json
{
  "content": "Content to analyze",
  "projectId": "project-123"
}
```

#### POST `/api/ai/draft`
```json
{
  "topic": "Sensor Integration",
  "projectId": "project-123",
  "style": "technical"
}
```

#### POST `/api/ai/plan`
```json
{
  "projectId": "project-123",
  "goals": ["goal1", "goal2"]
}
```

## 🔑 Authentication

All endpoints require API key authentication:

```http
X-API-Key: notebooker-api-key-2024
Content-Type: application/json
```

## 🌐 CORS Configuration

CORS is enabled for:
- `https://notebooker.netlify.app`
- `http://localhost:8080`
- `http://localhost:3000`

## 🧪 Testing

Run the test script locally:

```bash
python test_api.py
```

Or test with curl:

```bash
curl -X POST https://your-app.onrender.com/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: notebooker-api-key-2024" \
  -d '{"message": "Hello", "projectId": "test"}'
```

## 📊 Response Format

All endpoints return JSON in this format:

```json
{
  "success": true,
  "response": "AI generated content",
  "suggestions": ["suggestion1", "suggestion2"]
}
```

## 🔧 Troubleshooting

### Common Issues:

1. **Build fails**: Check Python version (3.11+)
2. **CORS errors**: Verify origins in app.py
3. **AI service errors**: Check AI_SERVICE_URL environment variable
4. **Authentication fails**: Verify X-API-Key header

### Logs:

Check Render logs for debugging:
- Go to your service → Logs tab
- Look for error messages and stack traces

## 🎯 Next Steps

1. **Deploy to Render** using the steps above
2. **Get your Render URL** (e.g., `https://ntbk-ai-flask-api.onrender.com`)
3. **Update your frontend** to use the real API endpoints
4. **Test the integration** with your Netlify frontend

## 📞 Support

If you encounter issues:
1. Check the Render logs
2. Verify environment variables
3. Test endpoints individually
4. Check CORS configuration
