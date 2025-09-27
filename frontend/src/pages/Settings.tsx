import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Bell, Shield, Palette, Database, Globe, Save, LogOut } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    navigate('/');
    toast.success('Logged out successfully');
  };

  if (loading) {
    return (
      <div className="cosmic-bg min-h-screen flex items-center justify-center">
        <div className="text-cosmic-white text-xl">Loading settings...</div>
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
              <h1 className="text-2xl font-bold text-cosmic-white">
                Settings
              </h1>
            </div>
            <button
              onClick={handleLogout}
              className="text-cosmic-bright hover:text-cosmic-white transition-colors flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Profile Settings */}
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <User className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-cosmic-white">Profile</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Username
                </label>
                <input
                  type="text"
                  defaultValue="Engineer"
                  className="cosmic-input w-full"
                />
              </div>
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Email
                </label>
                <input
                  type="email"
                  defaultValue="engineer@example.com"
                  className="cosmic-input w-full"
                />
              </div>
            </div>
          </div>

          {/* AI Settings */}
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Globe className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-cosmic-white">AI Configuration</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Model
                </label>
                <select className="cosmic-input w-full">
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3">Claude 3</option>
                </select>
              </div>
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Temperature: 0.7
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  defaultValue="0.7"
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="text-cosmic-white text-sm font-medium block mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  defaultValue="2000"
                  className="cosmic-input w-full"
                  min="100"
                  max="4000"
                />
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button className="cosmic-button flex items-center space-x-2">
              <Save className="w-4 h-4" />
              <span>Save Settings</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Settings;