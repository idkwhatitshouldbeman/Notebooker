import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'
import { useParams } from 'react-router-dom'

const Rewrite: React.FC = () => {
  const { sectionName } = useParams<{ sectionName: string }>()

  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">Rewrite Section</h1>
        <p className="page-subtitle">Section: {sectionName}</p>
      </div>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <h5>Section Rewriting</h5>
              <p className="text-muted">This page will contain the section rewriting functionality.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Rewrite
