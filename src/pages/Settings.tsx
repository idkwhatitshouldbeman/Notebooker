import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'

const Settings: React.FC = () => {
  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Configure your application settings</p>
      </div>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <h5>Application Settings</h5>
              <p className="text-muted">This page will contain the settings configuration.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Settings
