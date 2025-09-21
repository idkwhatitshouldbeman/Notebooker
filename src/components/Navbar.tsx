import React from 'react'
import { Navbar as BootstrapNavbar, Nav, Container, Button } from 'react-bootstrap'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../hooks/useAuthStore'
import { authAPI } from '../services/api'

const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('notebooker-auth')
      if (token) {
        const authData = JSON.parse(token)
        if (authData.state?.sessionToken) {
          await authAPI.logout(authData.state.sessionToken)
        }
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      logout()
      navigate('/auth')
    }
  }

  const isActive = (path: string) => {
    return location.pathname === path
  }

  return (
    <BootstrapNavbar bg="dark" variant="dark" expand="lg" className="border-bottom">
      <Container>
        <BootstrapNavbar.Brand as={Link} to="/">
          📓 Notebooker
        </BootstrapNavbar.Brand>
        
        <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
        
        <BootstrapNavbar.Collapse id="basic-navbar-nav">
          {isAuthenticated ? (
            <>
              <Nav className="me-auto">
                <Nav.Link as={Link} to="/dashboard" active={isActive('/dashboard')}>
                  Dashboard
                </Nav.Link>
                <Nav.Link as={Link} to="/sections" active={isActive('/sections')}>
                  Sections
                </Nav.Link>
                <Nav.Link as={Link} to="/analyze" active={isActive('/analyze')}>
                  Analyze
                </Nav.Link>
                <Nav.Link as={Link} to="/draft" active={isActive('/draft')}>
                  Draft
                </Nav.Link>
                <Nav.Link as={Link} to="/planning" active={isActive('/planning')}>
                  Planning
                </Nav.Link>
                <Nav.Link as={Link} to="/settings" active={isActive('/settings')}>
                  Settings
                </Nav.Link>
              </Nav>
              
              <Nav>
                <Navbar.Text className="me-3">
                  Welcome, {user?.username || 'User'}
                </Navbar.Text>
                <Button variant="outline-light" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </Nav>
            </>
          ) : (
            <Nav className="ms-auto">
              <Nav.Link as={Link} to="/auth" active={isActive('/auth')}>
                Login
              </Nav.Link>
            </Nav>
          )}
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  )
}

export default Navbar
