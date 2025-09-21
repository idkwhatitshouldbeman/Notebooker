import React from 'react'
import { Container, Row, Col, Card, Button } from 'react-bootstrap'
import { useParams, Link } from 'react-router-dom'

const ProjectWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1>Project Workspace - {id}</h1>
          <Card>
            <Card.Body>
              <p>Project workspace content will go here.</p>
              <div className="d-flex gap-2">
                <Button as={Link} to={`/project/${id}/sections`} variant="primary">
                  View Sections
                </Button>
                <Button as={Link} to={`/project/${id}/analyze`} variant="success">
                  AI Analysis
                </Button>
                <Button as={Link} to={`/project/${id}/draft`} variant="info">
                  AI Drafting
                </Button>
                <Button as={Link} to={`/project/${id}/rewrite`} variant="warning">
                  AI Rewrite
                </Button>
                <Button as={Link} to={`/project/${id}/planning`} variant="secondary">
                  Planning
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default ProjectWorkspace
