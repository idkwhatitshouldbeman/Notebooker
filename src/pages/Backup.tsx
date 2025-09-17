import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'

const Backup: React.FC = () => {
  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">Backup</h1>
        <p className="page-subtitle">Manage your data backups</p>
      </div>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <h5>Backup Management</h5>
              <p className="text-muted">This page will contain the backup functionality.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Backup
