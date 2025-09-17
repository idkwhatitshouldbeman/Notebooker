import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'
import { useParams } from 'react-router-dom'

const ViewSection: React.FC = () => {
  const { sectionName } = useParams<{ sectionName: string }>()

  return (
    <Container fluid>
      <div className="page-header">
        <h1 className="page-title">View Section</h1>
        <p className="page-subtitle">Section: {sectionName}</p>
      </div>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <h5>Section Content</h5>
              <p className="text-muted">This page will display the section content.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default ViewSection
