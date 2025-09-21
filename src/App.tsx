import React from 'react'
import { Container, Row, Col, Card } from 'react-bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {
  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1>📓 Notebooker</h1>
          <Card>
            <Card.Body>
              <p>Engineering Notebook Platform - Frontend Ready!</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default App
