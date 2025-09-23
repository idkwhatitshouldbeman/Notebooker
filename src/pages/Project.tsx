import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Brain, FileText, Edit3, Settings, Plus, MoreVertical, Calendar, User } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

interface Section {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'in-progress' | 'completed';
  lastModified: string;
  wordCount: number;
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

  useEffect(() => {
    if (id) {
      loadProject(id);
    }
  }, [id]);

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
    title: 'Robotics Control System',
    description: 'Advanced control algorithms for autonomous robot navigation and manipulation.',
    createdAt: '2024-01-15',
    lastModified: '2 days ago',
    sections: [
      {
        id: '1',
        title: 'System Architecture',
        content: 'Overview of the overall system design and component interactions...',
        status: 'completed',
        lastModified: '1 day ago',
        wordCount: 1250
      },
      {
        id: '2',
        title: 'Control Algorithms',
        content: 'Detailed implementation of PID controllers and path planning algorithms...',
        status: 'in-progress',
        lastModified: '2 days ago',
        wordCount: 890
      },
      {
        id: '3',
        title: 'Sensor Integration',
        content: 'Integration of LiDAR, cameras, and IMU sensors for environment perception...',
        status: 'draft',
        lastModified: '3 days ago',
        wordCount: 450
      },
      {
        id: '4',
        title: 'Testing & Validation',
        content: 'Test procedures and validation results for the control system...',
        status: 'draft',
        lastModified: '1 week ago',
        wordCount: 200
      }
    ]
  });

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

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button
            onClick={() => setShowCreateSection(true)}
            className="cosmic-button flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Section</span>
          </button>
          <Link
            to={`/project/${id}/analyze`}
            className="cosmic-button flex items-center space-x-2"
          >
            <Brain className="w-4 h-4" />
            <span>AI Analysis</span>
          </Link>
          <Link
            to={`/project/${id}/draft`}
            className="cosmic-button flex items-center space-x-2"
          >
            <Edit3 className="w-4 h-4" />
            <span>AI Draft</span>
          </Link>
          <Link
            to={`/project/${id}/planning`}
            className="cosmic-button flex items-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>Planning</span>
          </Link>
        </div>

        {/* Sections List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-cosmic-white mb-4">Project Sections</h2>
          {project.sections.map((section) => (
            <Link key={section.id} to={`/section/${section.id}`}>
              <div className="cosmic-card p-6 cursor-pointer group">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-lg">{getStatusIcon(section.status)}</span>
                      <h3 className="text-lg font-semibold text-cosmic-white group-hover:text-primary transition-colors">
                        {section.title}
                      </h3>
                      <span className={`text-sm font-medium ${getStatusColor(section.status)}`}>
                        {section.status.replace('-', ' ').toUpperCase()}
                      </span>
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
                  <button className="text-cosmic-bright hover:text-cosmic-white transition-colors">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </Link>
          ))}
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
