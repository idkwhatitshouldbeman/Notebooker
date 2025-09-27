import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

const NotFound: React.FC = () => {
  return (
    <div className="cosmic-bg min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-cosmic-white mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-cosmic-white mb-4">Page Not Found</h2>
        <p className="text-cosmic-bright mb-8">
          The page you're looking for doesn't exist in this cosmic dimension.
        </p>
        <div className="flex space-x-4 justify-center">
          <Link
            to="/dashboard"
            className="cosmic-button flex items-center space-x-2"
          >
            <Home className="w-4 h-4" />
            <span>Go Home</span>
          </Link>
          <button
            onClick={() => window.history.back()}
            className="px-4 py-2 text-cosmic-bright hover:text-cosmic-white transition-colors border border-cosmic-bright rounded-lg flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Go Back</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
