import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'

const Sections: React.FC = () => {
  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">Sections</h1>
        <p className="page-subtitle">Manage your engineering notebook sections</p>
      </div>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <h5>Sections Management</h5>
              <p className="text-muted">This page will contain the sections management functionality.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Sections
