import React from 'react'
import { Container, Row, Col, Card, Button } from 'react-bootstrap'
import { Link } from 'react-router-dom'

const Dashboard: React.FC = () => {
  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1 className="mb-4">📓 Notebooker Dashboard</h1>
          <p className="lead">Your Engineering Notebook Platform</p>
        </Col>
      </Row>
      
      <Row className="g-4">
        <Col md={6} lg={4}>
          <Card className="h-100 section-card">
            <Card.Body>
              <Card.Title>🚀 Create New Project</Card.Title>
              <Card.Text>
                Start a new engineering project and begin documenting your work.
              </Card.Text>
              <Button as={Link} to="/project/new" variant="primary">
                New Project
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6} lg={4}>
          <Card className="h-100 section-card">
            <Card.Body>
              <Card.Title>📊 AI Analysis</Card.Title>
              <Card.Text>
                Analyze your project content with AI-powered insights and suggestions.
              </Card.Text>
              <Button as={Link} to="/project/1/analyze" variant="success">
                Analyze Project
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6} lg={4}>
          <Card className="h-100 section-card">
            <Card.Body>
              <Card.Title>✍️ AI Drafting</Card.Title>
              <Card.Text>
                Use AI to help draft new content for your engineering notebook.
              </Card.Text>
              <Button as={Link} to="/project/1/draft" variant="info">
                Start Drafting
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6} lg={4}>
          <Card className="h-100 section-card">
            <Card.Body>
              <Card.Title>🔄 AI Rewrite</Card.Title>
              <Card.Text>
                Improve existing content with AI-powered rewriting and editing.
              </Card.Text>
              <Button as={Link} to="/project/1/rewrite" variant="warning">
                Rewrite Content
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6} lg={4}>
          <Card className="h-100 section-card">
            <Card.Body>
              <Card.Title>📋 Project Planning</Card.Title>
              <Card.Text>
                Plan your project structure and organize your engineering workflow.
              </Card.Text>
              <Button as={Link} to="/project/1/planning" variant="secondary">
                Plan Project
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6} lg={4}>
          <Card className="h-100 section-card">
            <Card.Body>
              <Card.Title>💾 Backup & Restore</Card.Title>
              <Card.Text>
                Backup your work and restore from previous versions.
              </Card.Text>
              <Button as={Link} to="/backup" variant="outline-primary">
                Manage Backups
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row className="mt-5">
        <Col>
          <Card>
            <Card.Header>
              <h5>🎯 Recent Projects</h5>
            </Card.Header>
            <Card.Body>
              <p className="text-muted">No recent projects found. Create your first project to get started!</p>
              <Button as={Link} to="/project/new" variant="primary">
                Create Your First Project
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Dashboard
