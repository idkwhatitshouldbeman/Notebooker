import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Pencil, Clock, CheckCircle, MoreVertical, Settings, LogOut, BookOpen, Brain, FileText } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

interface ProjectStats {
  started: number;
  inProgress: number;
  finished: number;
}

interface Project {
  id: string;
  title: string;
  summary: string;
  stats: ProjectStats;
  lastModified: string;
  status: 'active' | 'archived' | 'draft';
}

const Dashboard: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProject, setNewProject] = useState({ title: '', summary: '' });
  const navigate = useNavigate();

  // Load projects from backend
  useEffect(() => {
    console.log('🏠 Dashboard component mounted');
    console.log('🔍 Checking authentication status...');
    
    const authToken = localStorage.getItem('authToken');
    const username = localStorage.getItem('username');
    const authTimestamp = localStorage.getItem('authTimestamp');
    
    console.log('🔐 Auth status:', {
      hasToken: !!authToken,
      username: username,
      authTimestamp: authTimestamp ? new Date(parseInt(authTimestamp)).toISOString() : null,
      tokenPreview: authToken ? authToken.substring(0, 20) + '...' : null
    });

    if (!authToken) {
      console.warn('⚠️ No auth token found, redirecting to login');
      navigate('/');
      return;
    }

    loadProjects();
  }, []);

  const loadProjects = async () => {
    console.log('📂 Loading projects...');
    try {
      console.log('🌐 Attempting to fetch projects from API...');
      const response = await axios.get('https://ntbk-ai.onrender.com/api/projects', {
        headers: {
          'X-API-Key': 'notebooker-api-key-2024'
        }
      });
      console.log('✅ API response received:', response.data);
      
      if (response.data.success) {
        console.log('📋 Projects loaded from API:', response.data.projects?.length || 0);
        setProjects(response.data.projects || []);
      } else {
        console.warn('⚠️ API returned unsuccessful response, using sample data');
        setProjects(getSampleProjects());
      }
    } catch (error: any) {
      console.error('❌ Error loading projects from API:', {
        error: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.config?.url
      });
      
      console.log('🔄 Falling back to sample data...');
      setProjects(getSampleProjects());
      toast.error('Using offline mode - some features may be limited');
    } finally {
      setLoading(false);
      console.log('🏁 Project loading completed');
    }
  };

  const getSampleProjects = (): Project[] => [
    {
      id: '1',
      title: 'AI-Powered Engineering Notebook',
      summary: 'A comprehensive engineering documentation system with AI assistance for technical writing, analysis, and project management.',
      stats: { started: 8, inProgress: 3, finished: 12 },
      lastModified: '2 hours ago',
      status: 'active'
    }
  ];

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProject.title.trim()) {
      toast.error('Project title is required');
      return;
    }

    try {
      const response = await axios.post('/api/projects', {
        title: newProject.title,
        summary: newProject.summary
      });

      if (response.data.success) {
        toast.success('Project created successfully!');
        setNewProject({ title: '', summary: '' });
        setShowCreateModal(false);
        loadProjects();
      } else {
        toast.error('Failed to create project');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project. Please try again.');
    }
  };

  const handleLogout = () => {
    console.log('🚪 User signing out...');
    
    const authToken = localStorage.getItem('authToken');
    const username = localStorage.getItem('username');
    
    console.log('🔐 Clearing auth data:', {
      hadToken: !!authToken,
      username: username
    });
    
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    localStorage.removeItem('authTimestamp');
    
    console.log('✅ Auth data cleared, redirecting to login');
    toast.success('Logged out successfully');
    navigate('/');
  };

  const StatIcon: React.FC<{ type: 'started' | 'inProgress' | 'finished' }> = ({ type }) => {
    switch (type) {
      case 'started':
        return <Pencil className="w-4 h-4 text-warning" />;
      case 'inProgress':
        return <Clock className="w-4 h-4 text-primary" />;
      case 'finished':
        return <CheckCircle className="w-4 h-4 text-success" />;
    }
  };

  if (loading) {
    return (
      <div className="cosmic-bg min-h-screen flex items-center justify-center">
        <div className="text-cosmic-white text-xl">Loading your projects...</div>
      </div>
    );
  }

  return (
    <div className="cosmic-bg min-h-screen">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-cosmic-white tracking-wider">
              NOTEBOOKR
            </h1>
            <div className="flex items-center space-x-4">
              <Link 
                to="/settings"
                className="text-cosmic-bright hover:text-cosmic-white transition-colors flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </Link>
              <button
                onClick={handleLogout}
                className="text-cosmic-bright hover:text-cosmic-white transition-colors flex items-center space-x-2 text-sm"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-semibold text-cosmic-white mb-2">
              Your Engineering Projects
            </h2>
            <p className="text-cosmic-bright">
              Continue your engineering journey or start something new
            </p>
          </div>
          <div className="flex space-x-4">
            <Link
              to="/backup"
              className="cosmic-button flex items-center space-x-2"
            >
              <FileText className="w-4 h-4" />
              <span>Backup</span>
            </Link>
          </div>
        </div>

        {/* Projects Grid */}
        <div className="project-grid">
          {/* Add New Project Card */}
          <div 
            className="cosmic-card p-6 border-2 border-dashed border-input-border hover:border-primary transition-colors cursor-pointer group"
            onClick={() => setShowCreateModal(true)}
          >
            <div className="flex flex-col items-center justify-center h-48 space-y-4">
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center group-hover:bg-primary/30 transition-colors">
                <Plus className="w-6 h-6 text-primary" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-cosmic-white mb-1">
                  New Project
                </h3>
                <p className="text-cosmic-bright text-sm">
                  Start your next engineering adventure
                </p>
              </div>
            </div>
          </div>

          {/* Existing Projects */}
          {projects.map((project) => (
            <Link key={project.id} to={`/project/${project.id}`}>
              <div className="cosmic-card p-6 h-full cursor-pointer group">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-xl font-semibold text-cosmic-white group-hover:text-primary transition-colors line-clamp-2">
                    {project.title}
                  </h3>
                  <button className="text-cosmic-bright hover:text-cosmic-white transition-colors">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>

                <p className="text-cosmic-bright text-sm mb-6 line-clamp-3">
                  {project.summary}
                </p>

                {/* Stats */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <StatIcon type="started" />
                      <span className="text-cosmic-bright">Started:</span>
                    </div>
                    <span className="text-cosmic-white font-medium">{project.stats.started}</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <StatIcon type="inProgress" />
                      <span className="text-cosmic-bright">In Progress:</span>
                    </div>
                    <span className="text-cosmic-white font-medium">{project.stats.inProgress}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <StatIcon type="finished" />
                      <span className="text-cosmic-bright">Finished:</span>
                    </div>
                    <span className="text-cosmic-white font-medium">{project.stats.finished}</span>
                  </div>
                </div>

                {/* Last Modified */}
                <div className="pt-4 border-t border-border">
                  <p className="text-cosmic-bright text-xs">
                    Last modified {project.lastModified}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="cosmic-card p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-cosmic-white mb-4">Create New Project</h3>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Project Title
                </label>
                <input
                  type="text"
                  value={newProject.title}
                  onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                  className="cosmic-input w-full"
                  placeholder="Enter project title"
                  required
                />
              </div>
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Description
                </label>
                <textarea
                  value={newProject.summary}
                  onChange={(e) => setNewProject({ ...newProject, summary: e.target.value })}
                  className="cosmic-input w-full h-20 resize-none"
                  placeholder="Enter project description"
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="cosmic-button flex-1"
                >
                  Create Project
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
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

export default Dashboard;