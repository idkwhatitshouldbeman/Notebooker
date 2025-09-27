import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit3, Save, FileText, Calendar } from 'lucide-react';
import { toast } from 'sonner';

const ViewSection: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(`# System Architecture

## Overview
This document outlines the overall system design and component interactions for the robotics control system.

## Components
- **Main Controller**: Central processing unit for all control decisions
- **Sensor Interface**: Handles input from various sensors
- **Actuator Control**: Manages motor and servo control
- **Communication Module**: Handles external communication

## Data Flow
1. Sensors collect environmental data
2. Data is processed by the main controller
3. Control decisions are made based on algorithms
4. Commands are sent to actuators
5. System state is updated and logged

## Performance Requirements
- Response time: < 10ms
- Accuracy: 99.9%
- Uptime: 99.5%`);

  const handleSave = () => {
    toast.success('Section saved successfully!');
    setEditing(false);
  };

  return (
    <div className="cosmic-bg min-h-screen">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="text-cosmic-bright hover:text-cosmic-white transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <h1 className="text-2xl font-bold text-cosmic-white">Section View</h1>
            </div>
            <div className="flex items-center space-x-4">
              {editing ? (
                <button onClick={handleSave} className="cosmic-button flex items-center space-x-2">
                  <Save className="w-4 h-4" />
                  <span>Save</span>
                </button>
              ) : (
                <button onClick={() => setEditing(true)} className="cosmic-button flex items-center space-x-2">
                  <Edit3 className="w-4 h-4" />
                  <span>Edit</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="cosmic-card p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <FileText className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-cosmic-white">System Architecture</h2>
            </div>
            <div className="flex items-center space-x-2 text-sm text-cosmic-bright">
              <Calendar className="w-4 h-4" />
              <span>Last modified: 2 days ago</span>
            </div>
          </div>

          {editing ? (
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="cosmic-input w-full h-96 resize-none font-mono text-sm"
            />
          ) : (
            <div className="prose prose-invert max-w-none">
              <pre className="text-cosmic-white whitespace-pre-wrap font-mono text-sm leading-relaxed">
                {content}
              </pre>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default ViewSection;