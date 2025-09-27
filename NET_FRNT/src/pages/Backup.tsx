import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Upload, Database, Cloud, HardDrive } from 'lucide-react';
import { toast } from 'sonner';

const Backup: React.FC = () => {
  const navigate = useNavigate();
  const [backingUp, setBackingUp] = useState(false);
  const [restoring, setRestoring] = useState(false);

  const handleBackup = async () => {
    setBackingUp(true);
    // Simulate backup process
    setTimeout(() => {
      setBackingUp(false);
      toast.success('Backup completed successfully!');
    }, 3000);
  };

  const handleRestore = async () => {
    setRestoring(true);
    // Simulate restore process
    setTimeout(() => {
      setRestoring(false);
      toast.success('Restore completed successfully!');
    }, 3000);
  };

  return (
    <div className="cosmic-bg min-h-screen">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-cosmic-bright hover:text-cosmic-white transition-colors"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h1 className="text-2xl font-bold text-cosmic-white">Backup & Restore</h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="space-y-6">
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Database className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-cosmic-white">Data Management</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-cosmic-white font-medium">Create Backup</h3>
                <p className="text-cosmic-bright text-sm">
                  Export all your projects and data to a local file for safekeeping.
                </p>
                <button
                  onClick={handleBackup}
                  disabled={backingUp}
                  className="cosmic-button w-full flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {backingUp ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Backing up...</span>
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      <span>Download Backup</span>
                    </>
                  )}
                </button>
              </div>

              <div className="space-y-4">
                <h3 className="text-cosmic-white font-medium">Restore from Backup</h3>
                <p className="text-cosmic-bright text-sm">
                  Import previously exported data to restore your projects.
                </p>
                <button
                  onClick={handleRestore}
                  disabled={restoring}
                  className="cosmic-button w-full flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {restoring ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Restoring...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      <span>Upload Backup</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Cloud className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-cosmic-white">Cloud Sync</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-cosmic-white font-medium">Auto Sync</h3>
                  <p className="text-cosmic-bright text-sm">Automatically sync your data to the cloud</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-cosmic-white font-medium">Last Sync</h3>
                  <p className="text-cosmic-bright text-sm">2 hours ago</p>
                </div>
                <button className="cosmic-button">
                  Sync Now
                </button>
              </div>
            </div>
          </div>

          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <HardDrive className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-cosmic-white">Storage Info</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-cosmic-white">Projects</span>
                <span className="text-cosmic-bright">6 projects</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-cosmic-white">Total Size</span>
                <span className="text-cosmic-bright">2.4 MB</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-cosmic-white">Last Backup</span>
                <span className="text-cosmic-bright">1 day ago</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Backup;