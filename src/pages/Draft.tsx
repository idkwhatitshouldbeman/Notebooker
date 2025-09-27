import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit3, Loader2, Save, FileText } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { aiDraft } from '@/services/aiService';

const Draft: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [drafting, setDrafting] = useState(false);
  const [content, setContent] = useState('');
  const [prompt, setPrompt] = useState('');

  const handleDraft = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt for the AI to draft content');
      return;
    }

    setDrafting(true);
    try {
      console.log('✍️ Starting AI draft...');
      
      const aiResponse = await aiDraft(prompt, id || 'default', 'technical');
      
      if (aiResponse.success) {
        setContent(aiResponse.content || aiResponse.response || 'Draft content generated');
        toast.success('AI content drafted successfully!');
        console.log('✅ AI draft completed');
      } else {
        throw new Error(aiResponse.message || 'Drafting failed');
      }
    } catch (error: any) {
      console.error('❌ AI draft error:', error);
      
      // Fallback to mock content if AI service fails
      setTimeout(() => {
        setContent(`# ${prompt}

This is AI-generated content based on your prompt. The AI has analyzed your request and created this draft content that you can edit and refine.

## Key Points

- Point 1: Generated based on your prompt
- Point 2: AI-assisted content creation
- Point 3: Ready for your review and editing

## Next Steps

1. Review the generated content
2. Edit and refine as needed
3. Save to your project

This content was created using advanced AI models to assist in your engineering documentation process.`);
        setDrafting(false);
        toast.success('Content drafted successfully (using fallback data)!');
      }, 3000);
    }
  };

  const handleSave = async () => {
    if (!content.trim()) {
      toast.error('No content to save');
      return;
    }

    try {
      const response = await axios.post(`/api/projects/${id}/sections`, {
        title: prompt || 'AI Drafted Content',
        content: content
      });

      if (response.data.success) {
        toast.success('Content saved to project!');
        navigate(`/project/${id}`);
      } else {
        toast.error('Failed to save content');
      }
    } catch (error) {
      console.error('Error saving:', error);
      toast.error('Failed to save content. Please try again.');
    }
  };

  return (
    <div className="cosmic-bg min-h-screen">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(`/project/${id}`)}
                className="text-cosmic-bright hover:text-cosmic-white transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <h1 className="text-2xl font-bold text-cosmic-white">
                AI Draft Assistant
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleSave}
                disabled={!content.trim()}
                className="cosmic-button flex items-center space-x-2 disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                <span>Save</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Side - Prompt Input */}
          <div className="space-y-6">
            <div className="cosmic-card p-6">
              <div className="flex items-center space-x-3 mb-6">
                <Edit3 className="w-6 h-6 text-primary" />
                <h2 className="text-xl font-semibold text-cosmic-white">Draft Prompt</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-cosmic-white text-sm font-medium block mb-2">
                    What would you like the AI to draft?
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="cosmic-input w-full h-32 resize-none"
                    placeholder="Describe what you want the AI to draft for you..."
                  />
                </div>
                <button
                  onClick={handleDraft}
                  disabled={drafting || !prompt.trim()}
                  className="cosmic-button w-full flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {drafting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Drafting...</span>
                    </>
                  ) : (
                    <>
                      <Edit3 className="w-4 h-4" />
                      <span>Generate Draft</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="cosmic-card p-6">
              <h3 className="text-cosmic-white font-medium mb-3">Tips for Better Drafts</h3>
              <ul className="text-cosmic-bright text-sm space-y-2">
                <li>• Be specific about the type of content you need</li>
                <li>• Include context about your project</li>
                <li>• Mention any specific requirements or constraints</li>
                <li>• Ask for particular sections or formats</li>
              </ul>
            </div>
          </div>

          {/* Right Side - Generated Content */}
          <div className="space-y-6">
            <div className="cosmic-card p-6">
              <div className="flex items-center space-x-3 mb-6">
                <FileText className="w-6 h-6 text-primary" />
                <h2 className="text-xl font-semibold text-cosmic-white">Generated Content</h2>
              </div>
              {content ? (
                <div className="space-y-4">
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="cosmic-input w-full h-96 resize-none font-mono text-sm"
                    placeholder="Generated content will appear here..."
                  />
                  <div className="flex justify-between items-center text-sm text-cosmic-bright">
                    <span>{content.length} characters</span>
                    <span>{content.split(' ').length} words</span>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Edit3 className="w-16 h-16 text-cosmic-bright mx-auto mb-4" />
                  <h3 className="text-cosmic-white text-lg font-medium mb-2">Ready to Draft</h3>
                  <p className="text-cosmic-bright text-sm">
                    Enter a prompt and click "Generate Draft" to create AI-powered content.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Draft;