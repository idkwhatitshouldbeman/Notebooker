import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'
import { useParams } from 'react-router-dom'

const ProjectWorkspace: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()

  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">Project Workspace</h1>
        <p className="page-subtitle">Project ID: {projectId}</p>
      </div>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <h5>Project Workspace</h5>
              <p className="text-muted">This page will contain the project workspace functionality.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default ProjectWorkspace
