import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'

const Settings: React.FC = () => {
  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1>Settings</h1>
          <Card>
            <Card.Body>
              <p>Application settings will be available here.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Settings
