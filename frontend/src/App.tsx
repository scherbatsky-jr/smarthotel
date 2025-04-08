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

function App() {
  const userInfo = localStorage.getItem("user_info");

  const handleLogout = () => {
    localStorage.removeItem("user_info");
    window.location.href = "/login";
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
              <Route path="/login" element={<LoginPage onLogin={() => window.location.href = "/"} />} />
              <Route path="/" element={<Home />} />
              <Route path="/login/guest" element={<LoginPage onLogin={() => window.location.href = "/guest"} />} />
              <Route path="/login/admin" element={<AdminLoginPage />} />
              <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
              <Route path="/guest/dashboard" element={<AssistantPage />} />
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