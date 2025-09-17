import React, { useState } from 'react'
import { Container, Row, Col, Card, Form, Button, Alert, Tab, Tabs } from 'react-bootstrap'
import { useAuthStore } from '../hooks/useAuthStore'
import { authAPI, LoginRequest, RegisterRequest } from '../services/api'

const AuthPage: React.FC = () => {
  const { login } = useAuthStore()
  const [activeTab, setActiveTab] = useState('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Login form state
  const [loginForm, setLoginForm] = useState<LoginRequest>({
    username: '',
    password: '',
  })

  // Register form state
  const [registerForm, setRegisterForm] = useState<RegisterRequest>({
    name: '',
    email: '',
    password: '',
  })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await authAPI.login(loginForm)
      
      if (response.success) {
        login(
          {
            id: response.user_id,
            username: response.username,
            email: loginForm.username, // Assuming username is email
          },
          response.session_token
        )
        setSuccess('Login successful!')
      } else {
        setError(response.error || 'Login failed')
      }
    } catch (error: any) {
      setError(error.response?.data?.error || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await authAPI.register(registerForm)
      
      if (response.success) {
        login(
          {
            id: response.user_id,
            username: response.username,
            email: registerForm.email,
          },
          response.session_token
        )
        setSuccess('Registration successful!')
      } else {
        setError(response.error || 'Registration failed')
      }
    } catch (error: any) {
      setError(error.response?.data?.error || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100">
      <Row className="w-100">
        <Col md={6} lg={4} className="mx-auto">
          <Card className="shadow">
            <Card.Body>
              <div className="text-center mb-4">
                <h2 className="text-primary">📓 Notebooker</h2>
                <p className="text-muted">Engineering Notebook Platform</p>
              </div>

              {error && <Alert variant="danger">{error}</Alert>}
              {success && <Alert variant="success">{success}</Alert>}

              <Tabs
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k || 'login')}
                className="mb-3"
              >
                <Tab eventKey="login" title="Login">
                  <Form onSubmit={handleLogin}>
                    <Form.Group className="mb-3">
                      <Form.Label>Username/Email</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Enter username or email"
                        value={loginForm.username}
                        onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                        required
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Password</Form.Label>
                      <Form.Control
                        type="password"
                        placeholder="Enter password"
                        value={loginForm.password}
                        onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                        required
                      />
                    </Form.Group>

                    <Button
                      variant="primary"
                      type="submit"
                      className="w-100"
                      disabled={loading}
                    >
                      {loading ? 'Logging in...' : 'Login'}
                    </Button>
                  </Form>
                </Tab>

                <Tab eventKey="register" title="Register">
                  <Form onSubmit={handleRegister}>
                    <Form.Group className="mb-3">
                      <Form.Label>Full Name</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Enter your full name"
                        value={registerForm.name}
                        onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                        required
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Gmail Address</Form.Label>
                      <Form.Control
                        type="email"
                        placeholder="Enter your Gmail address"
                        value={registerForm.email}
                        onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                        required
                      />
                      <Form.Text className="text-muted">
                        Only Gmail addresses are accepted
                      </Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Password</Form.Label>
                      <Form.Control
                        type="password"
                        placeholder="Enter password"
                        value={registerForm.password}
                        onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                        required
                      />
                    </Form.Group>

                    <Button
                      variant="primary"
                      type="submit"
                      className="w-100"
                      disabled={loading}
                    >
                      {loading ? 'Registering...' : 'Register'}
                    </Button>
                  </Form>
                </Tab>
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default AuthPage
