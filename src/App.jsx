import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [taskId, setTaskId] = useState('example-task-001');
  const [promptContext, setPromptContext] = useState('Analyze the key factors that determine whether a small business should invest in AI automation. Consider costs, benefits, risks, and implementation challenges. Provide a structured analysis with clear recommendations.');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1500);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const requestData = {
        task_id: taskId,
        prompt_context: promptContext,
        agent_config: {
          temperature: temperature,
          max_tokens: maxTokens,
          stop_sequences: ["\n\n---", "END_OF_ANALYSIS"],
          top_p: 0.9,
          frequency_penalty: 0.0,
          presence_penalty: 0.0
        },
        external_tool_endpoints: {
          web_search: "https://api.example.com/search",
          calculator: "https://api.example.com/calc",
          custom_tools: {
            business_analyzer: "https://api.example.com/business-analyzer"
          }
        }
      };

      const result = await axios.post('/api/agentic-task', requestData);
      setResponse(result.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 NTBK_AI Agentic Service</h1>
        <p>Powered by Google FLAN-T5 Small</p>
      </header>

      <main className="app-main">
        <div className="container">
          <div className="form-section">
            <h2>Submit Agentic Task</h2>
            <form onSubmit={handleSubmit} className="task-form">
              <div className="form-group">
                <label htmlFor="taskId">Task ID:</label>
                <input
                  type="text"
                  id="taskId"
                  value={taskId}
                  onChange={(e) => setTaskId(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="promptContext">Prompt Context:</label>
                <textarea
                  id="promptContext"
                  value={promptContext}
                  onChange={(e) => setPromptContext(e.target.value)}
                  rows="6"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="temperature">Temperature:</label>
                  <input
                    type="number"
                    id="temperature"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    min="0"
                    max="2"
                    step="0.1"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="maxTokens">Max Tokens:</label>
                  <input
                    type="number"
                    id="maxTokens"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    min="1"
                    max="4000"
                  />
                </div>
              </div>

              <button type="submit" disabled={loading} className="submit-btn">
                {loading ? 'Processing...' : 'Submit Task'}
              </button>
            </form>
          </div>

          {error && (
            <div className="error-section">
              <h3>❌ Error</h3>
              <div className="error-message">{error}</div>
            </div>
          )}

          {response && (
            <div className="response-section">
              <h3>✅ Response</h3>
              <div className="response-content">
                <div className="response-meta">
                  <p><strong>Task ID:</strong> {response.task_id}</p>
                  <p><strong>Status:</strong> <span className={`status ${response.status}`}>{response.status}</span></p>
                  {response.execution_time && (
                    <p><strong>Execution Time:</strong> {response.execution_time.toFixed(2)}s</p>
                  )}
                  {response.tokens_used && (
                    <p><strong>Tokens Used:</strong> {response.tokens_used}</p>
                  )}
                </div>

                <div className="response-body">
                  <h4>Agent Reply:</h4>
                  <div className="agent-reply">
                    {response.agent_reply}
                  </div>
                </div>

                {response.next_step && (
                  <div className="next-step">
                    <h4>Next Step:</h4>
                    <p><strong>Action:</strong> {response.next_step.action}</p>
                    <p><strong>Instructions:</strong> {response.next_step.instructions}</p>
                  </div>
                )}

                {response.logs && (
                  <div className="logs">
                    <h4>Execution Logs:</h4>
                    <pre className="logs-content">{response.logs}</pre>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
