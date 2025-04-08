import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AssistantPage from './pages/AssistantPage';
import LoginPage from './pages/LoginPage';
import Home from './pages/Home';
import AdminLoginPage from './pages/AdminLogin';
import AdminDashboardPage from './pages/AdminDashboard';

import "@fontsource/roboto";
import './App.scss';
import './assets/css/layout.scss';
import { Navbar, Row, Col, Container, Button } from 'react-bootstrap';
import { logout } from './services/authService';

function App() {
  const userInfo = JSON.parse(localStorage.getItem("user_info") || "null");

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  return (
    <Router>
      <Container fluid className="p-0 layout">
        <Row>
          <Col>
            <Navbar variant="dark" fixed="top" className="shadow-sm justify-content-between layout__navbar">
                <Container className="m-0 justify-content-between">
                  <Navbar.Brand href="/">Smart Hotel Assistant</Navbar.Brand>
                  {userInfo && (
                    <Button variant="outline-light" size="sm" onClick={handleLogout}>
                      Logout
                    </Button>
                  )}
                </Container>
            </Navbar>
          </Col>
        </Row>

        <Row className="layout__content">
          <Col>
            <Routes>
              <Route
                path="/login"
                element={userInfo ? <Navigate to="/" replace /> : <Navigate to="/login/guest" replace />}
              />
              <Route
                path="/login/guest"
                element={userInfo ? <Navigate to="/" replace /> : <LoginPage onLogin={() => window.location.href = "/guest/dashboard"} />}
              />
              <Route
                path="/login/admin"
                element={userInfo ? <Navigate to="/" replace /> : <AdminLoginPage />}
              />
              <Route
                path="/guest/dashboard"
                element={
                  userInfo && userInfo.role === "guest" ? (
                    <AssistantPage />
                  ) : (
                    <Navigate to="/login/guest" replace />
                  )
                }
              />
              <Route
                path="/admin/dashboard"
                element={
                  userInfo && userInfo.role === "admin" ? (
                    <AdminDashboardPage />
                  ) : (
                    <Navigate to="/login/admin" replace />
                  )
                }
              />
              <Route
                path="/"
                element={
                  userInfo ? (
                    userInfo.role === "admin" ? (
                      <Navigate to="/admin/dashboard" replace />
                    ) : (
                      <Navigate to="/guest/dashboard" replace />
                    )
                  ) : (
                    <Home />
                  )
                }
              />
            </Routes>
          </Col>
        </Row>

          <footer className="bg-dark text-white fixed-bottom py-3 mt-auto">
            <Container>
              <Row className="text-center">
                <Col>
                  <p className="mb-0">Made by Sunil Prajapati</p>
                </Col>
              </Row>
            </Container>
          </footer>
      </Container>
    </Router>
  );
}

export default App;