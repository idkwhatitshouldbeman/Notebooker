import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'

const Backup: React.FC = () => {
  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1>Backup & Restore</h1>
          <Card>
            <Card.Body>
              <p>Backup and restore tools will be available here.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Backup
