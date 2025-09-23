import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, CheckCircle, Clock, Plus } from 'lucide-react';
import { toast } from 'sonner';

const Planning: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([
    { id: 1, title: 'System Architecture Design', status: 'completed', priority: 'high' },
    { id: 2, title: 'Control Algorithm Implementation', status: 'in-progress', priority: 'high' },
    { id: 3, title: 'Sensor Integration', status: 'pending', priority: 'medium' },
    { id: 4, title: 'Testing & Validation', status: 'pending', priority: 'medium' }
  ]);
  const [newTask, setNewTask] = useState('');

  const addTask = () => {
    if (!newTask.trim()) {
      toast.error('Please enter a task title');
      return;
    }
    setTasks([...tasks, { id: Date.now(), title: newTask, status: 'pending', priority: 'low' }]);
    setNewTask('');
    toast.success('Task added successfully!');
  };

  const updateTaskStatus = (taskId: number, status: string) => {
    setTasks(tasks.map(task => task.id === taskId ? { ...task, status } : task));
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
            <h1 className="text-2xl font-bold text-cosmic-white">Project Planning</h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="space-y-6">
          <div className="cosmic-card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Calendar className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-cosmic-white">Project Tasks</h2>
            </div>
            
            <div className="space-y-4">
              {tasks.map((task) => (
                <div key={task.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => updateTaskStatus(task.id, task.status === 'completed' ? 'pending' : 'completed')}
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                        task.status === 'completed' ? 'bg-success border-success' : 'border-cosmic-bright'
                      }`}
                    >
                      {task.status === 'completed' && <CheckCircle className="w-3 h-3 text-white" />}
                    </button>
                    <div>
                      <h3 className={`text-cosmic-white ${task.status === 'completed' ? 'line-through opacity-60' : ''}`}>
                        {task.title}
                      </h3>
                      <div className="flex items-center space-x-2 text-sm text-cosmic-bright">
                        <span className={`px-2 py-1 rounded text-xs ${
                          task.priority === 'high' ? 'bg-error/20 text-error' :
                          task.priority === 'medium' ? 'bg-warning/20 text-warning' :
                          'bg-success/20 text-success'
                        }`}>
                          {task.priority}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${
                          task.status === 'completed' ? 'bg-success/20 text-success' :
                          task.status === 'in-progress' ? 'bg-warning/20 text-warning' :
                          'bg-cosmic-bright/20 text-cosmic-bright'
                        }`}>
                          {task.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex space-x-3">
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                className="cosmic-input flex-1"
                placeholder="Add new task..."
                onKeyPress={(e) => e.key === 'Enter' && addTask()}
              />
              <button onClick={addTask} className="cosmic-button flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Planning;