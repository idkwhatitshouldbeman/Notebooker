import React from 'react'
import { Container, Row, Col, Card, Button } from 'react-bootstrap'
import { useParams, Link } from 'react-router-dom'

const ViewSection: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1>View Section - {id}</h1>
          <Card>
            <Card.Body>
              <p>Section content will be displayed here.</p>
              <Button as={Link} to="/" variant="secondary">
                Back to Dashboard
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default ViewSection
