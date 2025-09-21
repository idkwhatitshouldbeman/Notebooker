# Netlify Deployment Guide

## Overview

This project is configured for deployment on Netlify with:
- **Frontend**: React + Vite application
- **Backend**: Netlify Functions (Python)
- **API**: Mock AI responses (FLAN-T5 model not included due to size constraints)

## Architecture

```
Frontend (React) → Netlify CDN → Netlify Functions (Python) → Mock AI Response
```

## Key Files

### Frontend
- `package.json` - Node.js dependencies
- `vite.config.js` - Vite build configuration
- `src/` - React application source
- `index.html` - Entry point with React root

### Backend
- `netlify/functions/agentic-task.py` - Main API endpoint
- `netlify/functions/health.py` - Health check endpoint
- `netlify/functions/requirements.txt` - Python dependencies (minimal)

### Configuration
- `netlify.toml` - Netlify deployment configuration
- `.gitignore` - Git ignore rules

## Deployment Process

1. **Build Frontend**: `npm install && npm run build`
2. **Deploy Functions**: Netlify automatically deploys Python functions
3. **Configure Redirects**: API calls routed to Netlify Functions
4. **Serve Static Files**: React app served from `dist/` directory

## API Endpoints

- `POST /api/agentic-task` - Submit agentic task (mock response)
- `GET /api/health` - Health check

## Limitations

- **No Real AI Model**: FLAN-T5 model too large for Netlify Functions
- **Mock Responses**: Returns simulated AI responses
- **Function Timeout**: 10-second execution limit
- **Memory Limit**: 128MB per function

## Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Production Deployment

1. Connect repository to Netlify
2. Set build command: `npm install && npm run build`
3. Set publish directory: `dist`
4. Deploy automatically on git push

## Environment Variables

No environment variables required for basic functionality.

## Troubleshooting

- **Build Fails**: Check Node.js version (18+)
- **Functions Timeout**: Reduce processing complexity
- **CORS Issues**: Check function headers
- **API Not Found**: Verify redirect rules in `netlify.toml`
