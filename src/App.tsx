import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Container } from 'react-bootstrap'
import { useAuthStore } from './hooks/useAuthStore'
import Navbar from './components/Navbar'
import AuthPage from './pages/AuthPage'
import Dashboard from './pages/Dashboard'
import ProjectWorkspace from './pages/ProjectWorkspace'
import Sections from './pages/Sections'
import Analyze from './pages/Analyze'
import Draft from './pages/Draft'
import Rewrite from './pages/Rewrite'
import ViewSection from './pages/ViewSection'
import Planning from './pages/Planning'
import Settings from './pages/Settings'
import Backup from './pages/Backup'
import './App.css'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="App">
      <Navbar />
      <Container fluid className="main-content">
        <Routes>
          <Route 
            path="/" 
            element={isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/auth" />} 
          />
          <Route path="/auth" element={<AuthPage />} />
          
          {isAuthenticated ? (
            <>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/project/:projectId" element={<ProjectWorkspace />} />
              <Route path="/sections" element={<Sections />} />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/draft" element={<Draft />} />
              <Route path="/rewrite/:sectionName" element={<Rewrite />} />
              <Route path="/section/:sectionName" element={<ViewSection />} />
              <Route path="/planning" element={<Planning />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/backup" element={<Backup />} />
            </>
          ) : (
            <Route path="*" element={<Navigate to="/auth" />} />
          )}
        </Routes>
      </Container>
    </div>
  )
}

export default App
