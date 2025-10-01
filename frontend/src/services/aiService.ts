import axios from 'axios';

// Render AI Service Configuration
const AI_SERVICE_URL = 'https://ntbk-ai.onrender.com';
const API_KEY = 'notebooker-api-key-2024';

// Wake up Render service (ping endpoint)
export const wakeUpAI = async () => {
  try {
    console.log('🔔 Pinging AI service to wake it up...');
    console.log('🌐 Target URL:', `${AI_SERVICE_URL}/health`);
    console.log('🔑 Using API Key:', API_KEY ? 'Present' : 'Missing');
    
    const response = await fetch(`${AI_SERVICE_URL}/health`, {
      method: 'GET',
      headers: {
        'X-API-Key': API_KEY,
      },
    });
    
    console.log('✅ AI service ping successful!');
    console.log('📊 Response status:', response.status);
    console.log('📊 Response headers:', Object.fromEntries(response.headers.entries()));
    
    return { success: true, status: response.status };
  } catch (error: any) {
    console.log('⚠️ AI service ping failed!');
    console.log('❌ Error type:', error.name);
    console.log('❌ Error message:', error.message);
    console.log('❌ Full error:', error);
    
    if (error.message.includes('CORS')) {
      console.log('🚨 CORS ERROR DETECTED: The AI service is not allowing requests from Netlify');
      console.log('🚨 SOLUTION: The other AI needs to add CORS support to their Flask app');
    } else if (error.message.includes('Failed to fetch')) {
      console.log('🚨 NETWORK ERROR: The AI service is completely down or unreachable');
      console.log('🚨 POSSIBLE CAUSES: Service crashed, domain changed, or network issue');
    }
    
    return { success: false, error: error.message };
  }
};

// Create axios instance with default headers
const aiService = axios.create({
  baseURL: AI_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
  timeout: 30000, // 30 second timeout for AI responses
});

// AI Chat endpoint
export const aiChat = async (message: string, projectId: string, context?: string) => {
  try {
    console.log('🤖 Sending AI chat request:', { message, projectId, context });
    
    const response = await aiService.post('/api/ai/chat', {
      message,
      projectId,
      context: context || 'Engineering project documentation'
    });
    
    console.log('✅ AI chat response received:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ AI chat error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'AI chat failed');
  }
};

// AI Analysis endpoint
export const aiAnalyze = async (content: string, projectId: string) => {
  try {
    console.log('🔍 Sending AI analysis request:', { content: content.substring(0, 100) + '...', projectId });
    
    const response = await aiService.post('/api/ai/analyze', {
      content,
      projectId
    });
    
    console.log('✅ AI analysis response received:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ AI analysis error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'AI analysis failed');
  }
};

// AI Draft endpoint
export const aiDraft = async (topic: string, projectId: string, style: string = 'technical') => {
  try {
    console.log('✍️ Sending AI draft request:', { topic, projectId, style });
    
    const response = await aiService.post('/api/ai/draft', {
      topic,
      projectId,
      style
    });
    
    console.log('✅ AI draft response received:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ AI draft error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'AI draft failed');
  }
};

// AI Planning endpoint
export const aiPlan = async (projectId: string, goals: string[]) => {
  try {
    console.log('📋 Sending AI planning request:', { projectId, goals });
    
    const response = await aiService.post('/api/ai/plan', {
      projectId,
      goals
    });
    
    console.log('✅ AI planning response received:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ AI planning error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'AI planning failed');
  }
};

export default aiService;
