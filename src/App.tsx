import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import 'bootstrap/dist/css/bootstrap.min.css'
import './App.css'

// Components
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import AuthPage from './pages/AuthPage'
import ProjectWorkspace from './pages/ProjectWorkspace'
import Sections from './pages/Sections'
import Analyze from './pages/Analyze'
import Draft from './pages/Draft'
import Rewrite from './pages/Rewrite'
import ViewSection from './pages/ViewSection'
import Planning from './pages/Planning'
import Settings from './pages/Settings'
import Backup from './pages/Backup'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Navbar />
          <main className="notebooker-container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/project/:id" element={<ProjectWorkspace />} />
              <Route path="/project/:id/sections" element={<Sections />} />
              <Route path="/project/:id/analyze" element={<Analyze />} />
              <Route path="/project/:id/draft" element={<Draft />} />
              <Route path="/project/:id/rewrite" element={<Rewrite />} />
              <Route path="/project/:id/planning" element={<Planning />} />
              <Route path="/section/:id" element={<ViewSection />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/backup" element={<Backup />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
