import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'

const Planning: React.FC = () => {
  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">Planning Sheet</h1>
        <p className="page-subtitle">Track your work progress and decisions</p>
      </div>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <h5>Planning Management</h5>
              <p className="text-muted">This page will contain the planning sheet functionality.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Planning
