import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Lock, Eye, EyeOff } from 'lucide-react';
import AnimatedBook from '@/components/AnimatedBook';
import { toast } from 'sonner';
import axios from 'axios';

const SignIn: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
  });
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (activeTab === 'signup' && formData.password !== formData.confirmPassword) {
        toast.error('Passwords do not match');
        setLoading(false);
        return;
      }

      const endpoint = activeTab === 'login' ? '/api/auth/login' : '/api/auth/register';
      const response = await axios.post(endpoint, {
        username: formData.username,
        password: formData.password
      });

      if (response.data.success) {
        toast.success(activeTab === 'login' ? 'Login successful!' : 'Account created successfully!');
        // Store auth token if provided
        if (response.data.token) {
          localStorage.setItem('authToken', response.data.token);
        }
        navigate('/dashboard');
      } else {
        toast.error(response.data.message || 'Authentication failed');
      }
    } catch (error: any) {
      console.error('Auth error:', error);
      if (error.response?.data?.message) {
        toast.error(error.response.data.message);
      } else {
        toast.error(activeTab === 'login' ? 'Login failed. Please try again.' : 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cosmic-bg min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold text-cosmic-white mb-4 tracking-wider">
            NOTEBOOKR
          </h1>
          <p className="text-cosmic-bright text-lg">
            AI-Assisted Engineering Notebook Platform
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Side - Form */}
          <div className="cosmic-card p-8 max-w-md mx-auto w-full">
            {/* Tabs */}
            <div className="flex space-x-2 mb-8">
              <button
                className={`cosmic-tab flex-1 ${activeTab === 'login' ? 'active' : ''}`}
                onClick={() => setActiveTab('login')}
              >
                Login
              </button>
              <button
                className={`cosmic-tab flex-1 ${activeTab === 'signup' ? 'active' : ''}`}
                onClick={() => setActiveTab('signup')}
              >
                Sign Up
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username Field */}
              <div className="space-y-2">
                <label className="text-cosmic-white text-sm font-medium">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-cosmic-bright w-5 h-5" />
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    className="cosmic-input w-full pl-12 pr-4"
                    placeholder="Enter your username"
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label className="text-cosmic-white text-sm font-medium">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-cosmic-bright w-5 h-5" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="cosmic-input w-full pl-12 pr-12"
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-cosmic-bright hover:text-cosmic-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {/* Confirm Password Field - Only for signup */}
              {activeTab === 'signup' && (
                <div className="space-y-2">
                  <label className="text-cosmic-white text-sm font-medium">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-cosmic-bright w-5 h-5" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="cosmic-input w-full pl-12 pr-4"
                      placeholder="Confirm your password"
                      required
                    />
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="cosmic-button w-full font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Processing...' : (activeTab === 'login' ? 'Login' : 'Create Account')}
              </button>

              {/* Forgot Password - Only show on login */}
              {activeTab === 'login' && (
                <div className="text-center">
                  <a 
                    href="#" 
                    className="text-cosmic-bright hover:text-cosmic-white transition-colors text-sm"
                  >
                    Forgot password?
                  </a>
                </div>
              )}
            </form>
          </div>

          {/* Right Side - Animated Book */}
          <div className="flex flex-col items-center justify-center">
            <AnimatedBook className="mb-8" />
            <p className="text-cosmic-bright text-center text-sm max-w-md">
              Click the magical book to experience the power of AI-assisted engineering documentation. 
              Watch as ancient runes transform into modern creativity.
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center">
          <div className="space-x-6">
            <a 
              href="#" 
              className="text-cosmic-bright hover:text-cosmic-white transition-colors text-sm"
            >
              Privacy Policy
            </a>
            <a 
              href="#" 
              className="text-cosmic-bright hover:text-cosmic-white transition-colors text-sm"
            >
              Terms of Service
            </a>
          </div>
          <p className="text-muted-foreground text-xs mt-4">
            © 2024 NOTEBOOKR. Crafted with cosmic energy.
          </p>
        </footer>
      </div>
    </div>
  );
};

export default SignIn;
