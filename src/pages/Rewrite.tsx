import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Loader2, Save } from 'lucide-react';
import { toast } from 'sonner';

const Rewrite: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [rewriting, setRewriting] = useState(false);
  const [originalContent, setOriginalContent] = useState('');
  const [rewrittenContent, setRewrittenContent] = useState('');

  const handleRewrite = async () => {
    if (!originalContent.trim()) {
      toast.error('Please enter content to rewrite');
      return;
    }

    setRewriting(true);
    // Simulate rewriting
    setTimeout(() => {
      setRewrittenContent(`# Rewritten Content

This is the AI-rewritten version of your content. The AI has improved clarity, structure, and flow while maintaining the original meaning.

## Key Improvements

- Enhanced readability and flow
- Better structure and organization
- Improved technical accuracy
- More engaging presentation

The rewritten content maintains all the essential information while presenting it in a more polished and professional manner.`);
      setRewriting(false);
      toast.success('Content rewritten successfully!');
    }, 3000);
  };

  return (
    <div className="cosmic-bg min-h-screen">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(`/project/${id}`)}
              className="text-cosmic-bright hover:text-cosmic-white transition-colors"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h1 className="text-2xl font-bold text-cosmic-white">AI Rewrite</h1>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="cosmic-card p-6">
            <h2 className="text-xl font-semibold text-cosmic-white mb-4">Original Content</h2>
            <textarea
              value={originalContent}
              onChange={(e) => setOriginalContent(e.target.value)}
              className="cosmic-input w-full h-96 resize-none"
              placeholder="Paste your content here to rewrite..."
            />
            <button
              onClick={handleRewrite}
              disabled={rewriting || !originalContent.trim()}
              className="cosmic-button w-full mt-4 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {rewriting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Rewriting...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  <span>Rewrite Content</span>
                </>
              )}
            </button>
          </div>

          <div className="cosmic-card p-6">
            <h2 className="text-xl font-semibold text-cosmic-white mb-4">Rewritten Content</h2>
            <textarea
              value={rewrittenContent}
              onChange={(e) => setRewrittenContent(e.target.value)}
              className="cosmic-input w-full h-96 resize-none"
              placeholder="Rewritten content will appear here..."
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Rewrite;