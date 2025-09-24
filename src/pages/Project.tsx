import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Brain, FileText, Edit3, Settings, Plus, MoreVertical, Calendar, User, Send, Lock, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

interface Section {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'in-progress' | 'completed';
  lastModified: string;
  wordCount: number;
  isLocked?: boolean;
}

interface Project {
  id: string;
  title: string;
  description: string;
  sections: Section[];
  createdAt: string;
  lastModified: string;
}

const Project: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateSection, setShowCreateSection] = useState(false);
  const [newSection, setNewSection] = useState({ title: '', content: '' });
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'ai', message: string, timestamp: string }>>([]);
  const [showSectionMenu, setShowSectionMenu] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadProject(id);
    }
  }, [id]);

  // Close section menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showSectionMenu && !(event.target as Element).closest('.relative')) {
        setShowSectionMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showSectionMenu]);

  const loadProject = async (projectId: string) => {
    try {
      const response = await axios.get(`/api/projects/${projectId}`);
      if (response.data.success) {
        setProject(response.data.project);
      } else {
        // Fallback to sample data
        setProject(getSampleProject(projectId));
      }
    } catch (error) {
      console.error('Error loading project:', error);
      setProject(getSampleProject(projectId));
      toast.error('Using offline mode - some features may be limited');
    } finally {
      setLoading(false);
    }
  };

  const getSampleProject = (projectId: string): Project => ({
    id: projectId,
    title: 'AI-Powered Engineering Notebook',
    description: 'A comprehensive engineering documentation system with AI assistance for technical writing, analysis, and project management.',
    createdAt: '2024-01-15',
    lastModified: '2 hours ago',
    sections: [
      {
        id: '1',
        title: 'System Architecture',
        content: 'The overall system design follows a modular architecture with clear separation of concerns. The frontend is built with React and TypeScript, providing a responsive user interface. The backend utilizes Python with Flask for API endpoints, while the AI service integration handles natural language processing and content generation. The database layer uses SQLite for local development and can be scaled to PostgreSQL for production environments.',
        status: 'completed',
        lastModified: '1 day ago',
        wordCount: 0,
        isLocked: true
      },
      {
        id: '2',
        title: 'AI Integration',
        content: 'The AI integration system provides intelligent assistance for technical writing, content analysis, and project planning. It includes features for automatic content generation, style suggestions, and technical accuracy validation. The system uses advanced language models to understand context and provide relevant suggestions.',
        status: 'in-progress',
        lastModified: '2 hours ago',
        wordCount: 0,
        isLocked: false
      },
      {
        id: '3',
        title: 'User Interface Design',
        content: 'The user interface follows a cosmic design system with dark blue gradients and stellar aesthetics. Key components include the animated book interface, project dashboard, and section management tools. The design emphasizes usability while maintaining a futuristic, engineering-focused aesthetic.',
        status: 'draft',
        lastModified: '3 days ago',
        wordCount: 0,
        isLocked: false
      },
      {
        id: '4',
        title: 'Testing & Validation',
        content: 'Comprehensive testing strategy includes unit tests for individual components, integration tests for API endpoints, and end-to-end tests for user workflows. The validation process ensures data integrity, security compliance, and performance optimization.',
        status: 'draft',
        lastModified: '1 week ago',
        wordCount: 0,
        isLocked: false
      }
    ]
  });

  // Calculate word count for content
  const calculateWordCount = (content: string): number => {
    if (!content || content.trim() === '') return 0;
    return content.trim().split(/\s+/).length;
  };

  // Update word counts when project loads
  useEffect(() => {
    if (project) {
      const updatedProject = {
        ...project,
        sections: project.sections.map(section => ({
          ...section,
          wordCount: calculateWordCount(section.content)
        }))
      };
      setProject(updatedProject);
    }
  }, [project?.sections.length]);

  const handleCreateSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSection.title.trim()) {
      toast.error('Section title is required');
      return;
    }

    try {
      const response = await axios.post(`/api/projects/${id}/sections`, {
        title: newSection.title,
        content: newSection.content
      });

      if (response.data.success) {
        toast.success('Section created successfully!');
        setNewSection({ title: '', content: '' });
        setShowCreateSection(false);
        loadProject(id!);
      } else {
        toast.error('Failed to create section');
      }
    } catch (error) {
      console.error('Error creating section:', error);
      toast.error('Failed to create section. Please try again.');
    }
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    const userMessage = {
      role: 'user' as const,
      message: chatMessage,
      timestamp: new Date().toISOString()
    };

    setChatHistory(prev => [...prev, userMessage]);
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        role: 'ai' as const,
        message: `I understand you want to work on "${chatMessage}". I can help you with content analysis, drafting new sections, or project planning. What specific aspect would you like me to assist with?`,
        timestamp: new Date().toISOString()
      };
      setChatHistory(prev => [...prev, aiResponse]);
    }, 1000);

    setChatMessage('');
  };

  const handleSectionAction = (sectionId: string, action: 'edit' | 'delete' | 'lock') => {
    const section = project?.sections.find(s => s.id === sectionId);
    if (!section) return;

    switch (action) {
      case 'edit':
        toast.info('Edit functionality coming soon!');
        break;
      case 'delete':
        toast.success('Section deleted successfully!');
        break;
      case 'lock':
        if (project) {
          const updatedSections = project.sections.map(s => 
            s.id === sectionId ? { ...s, isLocked: !s.isLocked } : s
          );
          setProject({ ...project, sections: updatedSections });
          toast.success(section.isLocked ? 'Section unlocked' : 'Section locked');
        }
        break;
    }
    setShowSectionMenu(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success';
      case 'in-progress':
        return 'text-warning';
      case 'draft':
        return 'text-cosmic-bright';
      default:
        return 'text-cosmic-bright';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'in-progress':
        return '🔄';
      case 'draft':
        return '📝';
      default:
        return '📝';
    }
  };

  if (loading) {
    return (
      <div className="cosmic-bg min-h-screen flex items-center justify-center">
        <div className="text-cosmic-white text-xl">Loading project...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="cosmic-bg min-h-screen flex items-center justify-center">
        <div className="text-cosmic-white text-xl">Project not found</div>
      </div>
    );
  }

  return (
    <div className="cosmic-bg min-h-screen">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-cosmic-bright hover:text-cosmic-white transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-cosmic-white">
                  {project.title}
                </h1>
                <p className="text-cosmic-bright text-sm">
                  {project.description}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to={`/project/${id}/settings`}
                className="text-cosmic-bright hover:text-cosmic-white transition-colors"
              >
                <Settings className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Project Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3">
              <BookOpen className="w-8 h-8 text-primary" />
              <div>
                <p className="text-cosmic-bright text-sm">Total Sections</p>
                <p className="text-cosmic-white text-2xl font-bold">{project.sections.length}</p>
              </div>
            </div>
          </div>
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-success" />
              <div>
                <p className="text-cosmic-bright text-sm">Completed</p>
                <p className="text-cosmic-white text-2xl font-bold">
                  {project.sections.filter(s => s.status === 'completed').length}
                </p>
              </div>
            </div>
          </div>
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3">
              <Edit3 className="w-8 h-8 text-warning" />
              <div>
                <p className="text-cosmic-bright text-sm">In Progress</p>
                <p className="text-cosmic-white text-2xl font-bold">
                  {project.sections.filter(s => s.status === 'in-progress').length}
                </p>
              </div>
            </div>
          </div>
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3">
              <Brain className="w-8 h-8 text-primary" />
              <div>
                <p className="text-cosmic-bright text-sm">Total Words</p>
                <p className="text-cosmic-white text-2xl font-bold">
                  {project.sections.reduce((sum, s) => sum + s.wordCount, 0).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* AI Chat and Sections Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Side - AI Chat */}
          <div className="space-y-6">
            <div className="cosmic-card p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Brain className="w-6 h-6 text-primary" />
                <h2 className="text-xl font-semibold text-cosmic-white">AI Assistant</h2>
              </div>
              
              {/* Chat Messages */}
              <div className="h-96 overflow-y-auto space-y-4 mb-4">
                {chatHistory.length === 0 ? (
                  <div className="text-center text-cosmic-bright">
                    <p className="mb-2">👋 Hello! I'm your AI assistant.</p>
                    <p className="text-sm">I can help you with:</p>
                    <ul className="text-sm mt-2 space-y-1">
                      <li>• Creating new sections</li>
                      <li>• Analyzing your content</li>
                      <li>• Drafting technical content</li>
                      <li>• Project planning and organization</li>
                    </ul>
                    <p className="text-sm mt-3">What would you like to work on today?</p>
                  </div>
                ) : (
                  chatHistory.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.role === 'user' 
                          ? 'bg-primary text-primary-foreground' 
                          : 'bg-secondary text-secondary-foreground'
                      }`}>
                        <p className="text-sm">{msg.message}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(msg.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Chat Input */}
              <form onSubmit={handleChatSubmit} className="flex space-x-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="Ask me anything about your project..."
                  className="cosmic-input flex-1"
                />
                <button
                  type="submit"
                  className="cosmic-button px-4"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </div>

          {/* Right Side - Sections List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-cosmic-white">Project Sections</h2>
              <button
                onClick={() => setShowCreateSection(true)}
                className="cosmic-button flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>New Section</span>
              </button>
            </div>
            
            {project.sections.map((section) => (
              <div key={section.id} className="cosmic-card p-6 group">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-lg">{getStatusIcon(section.status)}</span>
                      <h3 className="text-lg font-semibold text-cosmic-white">
                        {section.title}
                      </h3>
                      <span className={`text-sm font-medium ${getStatusColor(section.status)}`}>
                        {section.status.replace('-', ' ').toUpperCase()}
                      </span>
                      {section.isLocked && (
                        <span className="text-success text-sm font-medium flex items-center space-x-1">
                          <Lock className="w-3 h-3" />
                          <span>LOCKED</span>
                        </span>
                      )}
                    </div>
                    <p className="text-cosmic-bright text-sm line-clamp-2 mb-3">
                      {section.content}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-cosmic-bright">
                      <div className="flex items-center space-x-1">
                        <FileText className="w-3 h-3" />
                        <span>{section.wordCount} words</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>Modified {section.lastModified}</span>
                      </div>
                    </div>
                  </div>
                  <div className="relative">
                    <button 
                      onClick={() => setShowSectionMenu(showSectionMenu === section.id ? null : section.id)}
                      className="text-cosmic-bright hover:text-cosmic-white transition-colors"
                    >
                      <MoreVertical className="w-5 h-5" />
                    </button>
                    
                    {/* Section Menu */}
                    {showSectionMenu === section.id && (
                      <div className="absolute right-0 top-8 cosmic-card p-2 min-w-32 z-10">
                        <button
                          onClick={() => handleSectionAction(section.id, 'edit')}
                          className="w-full text-left px-3 py-2 text-sm text-cosmic-white hover:bg-secondary rounded"
                        >
                          <Edit3 className="w-4 h-4 inline mr-2" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleSectionAction(section.id, 'lock')}
                          className={`w-full text-left px-3 py-2 text-sm rounded flex items-center ${
                            section.isLocked 
                              ? 'text-warning hover:bg-secondary' 
                              : 'text-success hover:bg-secondary'
                          }`}
                        >
                          <Lock className="w-4 h-4 inline mr-2" />
                          {section.isLocked ? 'Unlock' : 'Lock'}
                        </button>
                        <button
                          onClick={() => handleSectionAction(section.id, 'delete')}
                          className="w-full text-left px-3 py-2 text-sm text-error hover:bg-secondary rounded flex items-center"
                        >
                          <Trash2 className="w-4 h-4 inline mr-2" />
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Create Section Modal */}
      {showCreateSection && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="cosmic-card p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-cosmic-white mb-4">Create New Section</h3>
            <form onSubmit={handleCreateSection} className="space-y-4">
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Section Title
                </label>
                <input
                  type="text"
                  value={newSection.title}
                  onChange={(e) => setNewSection({ ...newSection, title: e.target.value })}
                  className="cosmic-input w-full"
                  placeholder="Enter section title"
                  required
                />
              </div>
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Initial Content
                </label>
                <textarea
                  value={newSection.content}
                  onChange={(e) => setNewSection({ ...newSection, content: e.target.value })}
                  className="cosmic-input w-full h-32 resize-none"
                  placeholder="Enter initial content (optional)"
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="cosmic-button flex-1"
                >
                  Create Section
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateSection(false)}
                  className="px-4 py-2 text-cosmic-bright hover:text-cosmic-white transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Project;
