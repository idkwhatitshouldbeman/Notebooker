import React, { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Button, Alert, Spinner } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../hooks/useAuthStore'
import { projectAPI, aiAPI } from '../services/api'

const Dashboard: React.FC = () => {
  const { user } = useAuthStore()
  const [projects, setProjects] = useState<any[]>([])
  const [aiHealth, setAiHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load projects
      const projectsData = await projectAPI.getProjects()
      setProjects(projectsData)
      
      // Check AI service health
      const healthData = await aiAPI.healthCheck()
      setAiHealth(healthData)
      
    } catch (error: any) {
      setError('Failed to load dashboard data')
      console.error('Dashboard error:', error)
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    {
      title: 'Create New Section',
      description: 'Draft a new engineering section with AI assistance',
      icon: '📝',
      link: '/draft',
      color: 'primary'
    },
    {
      title: 'Analyze Content',
      description: 'Analyze existing sections for gaps and improvements',
      icon: '🔍',
      link: '/analyze',
      color: 'info'
    },
    {
      title: 'View Sections',
      description: 'Browse and manage your engineering sections',
      icon: '📚',
      link: '/sections',
      color: 'success'
    },
    {
      title: 'Planning Sheet',
      description: 'Track your work progress and decisions',
      icon: '📋',
      link: '/planning',
      color: 'warning'
    }
  ]

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-3">Loading dashboard...</p>
      </Container>
    )
  }

  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">
          Welcome back, {user?.username}! Manage your engineering projects and documentation.
        </p>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* AI Service Status */}
      {aiHealth && (
        <Row className="mb-4">
          <Col>
            <Card className={aiHealth.healthy ? 'border-success' : 'border-warning'}>
              <Card.Body>
                <div className="d-flex align-items-center">
                  <div className="me-3">
                    {aiHealth.healthy ? '✅' : '⚠️'}
                  </div>
                  <div>
                    <h6 className="mb-1">AI Service Status</h6>
                    <p className="mb-0 text-muted">
                      {aiHealth.healthy ? 'AI service is available' : 'AI service is unavailable - using fallback mode'}
                    </p>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Quick Actions */}
      <Row className="mb-4">
        <Col>
          <h4>Quick Actions</h4>
        </Col>
      </Row>
      
      <Row className="mb-5">
        {quickActions.map((action, index) => (
          <Col md={6} lg={3} key={index} className="mb-3">
            <Card className="feature-card h-100">
              <Card.Body className="text-center">
                <div className="feature-icon">{action.icon}</div>
                <h5 className="card-title">{action.title}</h5>
                <p className="card-text text-muted">{action.description}</p>
                <Button 
                  as={Link} 
                  to={action.link} 
                  variant={action.color as any}
                  className="btn-action"
                >
                  Get Started
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Recent Projects */}
      <Row>
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h4>Recent Projects</h4>
            <Button as={Link} to="/projects/new" variant="outline-primary">
              New Project
            </Button>
          </div>
        </Col>
      </Row>

      <Row>
        {projects.length > 0 ? (
          projects.slice(0, 4).map((project) => (
            <Col md={6} lg={3} key={project.id} className="mb-3">
              <Card className="h-100">
                <Card.Body>
                  <h6 className="card-title">{project.name}</h6>
                  <p className="card-text text-muted small">
                    {project.description || 'No description available'}
                  </p>
                  <div className="d-flex justify-content-between align-items-center">
                    <span className={`status-badge status-${project.status === 'active' ? 'active' : 'pending'}`}>
                      {project.status}
                    </span>
                    <Button 
                      as={Link} 
                      to={`/project/${project.id}`} 
                      variant="outline-primary" 
                      size="sm"
                    >
                      Open
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))
        ) : (
          <Col>
            <Card>
              <Card.Body className="text-center py-5">
                <h5 className="text-muted">No projects yet</h5>
                <p className="text-muted">Create your first project to get started</p>
                <Button as={Link} to="/projects/new" variant="primary">
                  Create Project
                </Button>
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>
    </Container>
  )
}

export default Dashboard
