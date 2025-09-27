import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Brain, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { aiAnalyze } from '@/services/aiService';

const Analyze: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [selectedSections, setSelectedSections] = useState<string[]>([]);

  const sampleSections = [
    { id: '1', title: 'System Architecture', content: 'Overview of the overall system design...' },
    { id: '2', title: 'Control Algorithms', content: 'Detailed implementation of PID controllers...' },
    { id: '3', title: 'Sensor Integration', content: 'Integration of LiDAR, cameras, and IMU sensors...' },
    { id: '4', title: 'Testing & Validation', content: 'Test procedures and validation results...' }
  ];

  const handleAnalyze = async () => {
    if (selectedSections.length === 0) {
      toast.error('Please select at least one section to analyze');
      return;
    }

    setAnalyzing(true);
    try {
      console.log('🔍 Starting AI analysis...');
      
      // Get content from selected sections
      const contentToAnalyze = sampleSections
        .filter(section => selectedSections.includes(section.id))
        .map(section => `${section.title}: ${section.content}`)
        .join('\n\n');

      const aiResponse = await aiAnalyze(contentToAnalyze, id || 'default');
      
      if (aiResponse.success) {
        setAnalysis(aiResponse);
        toast.success('AI analysis completed successfully!');
        console.log('✅ AI analysis completed');
      } else {
        throw new Error(aiResponse.message || 'Analysis failed');
      }
    } catch (error: any) {
      console.error('❌ AI analysis error:', error);
      
      // Fallback to mock analysis if AI service fails
      setTimeout(() => {
        setAnalysis({
          gaps: [
            { section: 'System Architecture', gap: 'Missing error handling mechanisms' },
            { section: 'Control Algorithms', gap: 'No performance metrics defined' }
          ],
          suggestions: [
            'Add comprehensive error handling to system architecture',
            'Define clear performance metrics for control algorithms',
            'Include scalability considerations in sensor integration'
          ],
          questions: [
            'What are the expected performance requirements?',
            'How will the system handle sensor failures?',
            'What is the expected system uptime?'
          ]
        });
        setAnalyzing(false);
        toast.success('Analysis completed (using fallback data)!');
      }, 3000);
    }
  };

  const toggleSection = (sectionId: string) => {
    setSelectedSections(prev => 
      prev.includes(sectionId) 
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
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
                AI Analysis
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Side - Section Selection */}
          <div className="space-y-6">
            <div className="cosmic-card p-6">
              <div className="flex items-center space-x-3 mb-6">
                <FileText className="w-6 h-6 text-primary" />
                <h2 className="text-xl font-semibold text-cosmic-white">Select Sections</h2>
              </div>
              <div className="space-y-3">
                {sampleSections.map((section) => (
                  <div
                    key={section.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedSections.includes(section.id)
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50'
                    }`}
                    onClick={() => toggleSection(section.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={selectedSections.includes(section.id)}
                        onChange={() => toggleSection(section.id)}
                        className="w-4 h-4 text-primary"
                      />
                      <div>
                        <h3 className="text-cosmic-white font-medium">{section.title}</h3>
                        <p className="text-cosmic-bright text-sm line-clamp-2">{section.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="cosmic-card p-6">
              <button
                onClick={handleAnalyze}
                disabled={analyzing || selectedSections.length === 0}
                className="cosmic-button w-full flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4" />
                    <span>Analyze Selected Sections</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Side - Analysis Results */}
          <div className="space-y-6">
            {analysis && (
              <>
                {/* Gaps Analysis */}
                <div className="cosmic-card p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <AlertCircle className="w-6 h-6 text-warning" />
                    <h2 className="text-xl font-semibold text-cosmic-white">Identified Gaps</h2>
                  </div>
                  <div className="space-y-3">
                    {analysis.gaps?.map((gap: any, index: number) => (
                      <div key={index} className="p-3 bg-warning/10 border border-warning/20 rounded-lg">
                        <p className="text-cosmic-white font-medium">{gap.section}</p>
                        <p className="text-cosmic-bright text-sm">{gap.gap}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Suggestions */}
                <div className="cosmic-card p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-success" />
                    <h2 className="text-xl font-semibold text-cosmic-white">Suggestions</h2>
                  </div>
                  <div className="space-y-3">
                    {analysis.suggestions?.map((suggestion: string, index: number) => (
                      <div key={index} className="p-3 bg-success/10 border border-success/20 rounded-lg">
                        <p className="text-cosmic-white text-sm">{suggestion}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Questions */}
                <div className="cosmic-card p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <Brain className="w-6 h-6 text-primary" />
                    <h2 className="text-xl font-semibold text-cosmic-white">Questions to Consider</h2>
                  </div>
                  <div className="space-y-3">
                    {analysis.questions?.map((question: string, index: number) => (
                      <div key={index} className="p-3 bg-primary/10 border border-primary/20 rounded-lg">
                        <p className="text-cosmic-white text-sm">{question}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {!analysis && !analyzing && (
              <div className="cosmic-card p-6">
                <div className="text-center py-12">
                  <Brain className="w-16 h-16 text-cosmic-bright mx-auto mb-4" />
                  <h3 className="text-cosmic-white text-lg font-medium mb-2">Ready to Analyze</h3>
                  <p className="text-cosmic-bright text-sm">
                    Select sections from your project and click "Analyze" to get AI-powered insights.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Analyze;