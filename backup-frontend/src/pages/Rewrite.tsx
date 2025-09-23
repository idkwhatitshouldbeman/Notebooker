import React from 'react'
import { Container, Row, Col, Card, Button } from 'react-bootstrap'
import { useParams, Link } from 'react-router-dom'

const Rewrite: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1>AI Rewrite - Project {id}</h1>
          <Card>
            <Card.Body>
              <p>AI rewriting tools will be available here.</p>
              <Button as={Link} to={`/project/${id}`} variant="secondary">
                Back to Project
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Rewrite
