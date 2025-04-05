import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AssistantPage from './pages/AssistantPage';
import LoginPage from './pages/LoginPage';

import './App.scss';
import './assets/css/layout.scss';
import { Navbar, Row, Col, Container } from 'react-bootstrap';

function App() {
  const userInfo = localStorage.getItem("user_info");

  return (
    <Router>
      <Container fluid className="p-0">
        <Row>
          <Col>
            <Navbar bg="primary" variant="dark" fixed="top" className="shadow-sm">
              <Container className="m-0">
                <Navbar.Brand href="/">SmartHotel Assistant</Navbar.Brand>
              </Container>
            </Navbar>
          </Col>
        </Row>

        <Row className="layout__content mt-5">
          <Col>
            <Routes>
              <Route path="/login" element={<LoginPage onLogin={() => window.location.href = "/"} />} />
              <Route
                path="/"
                element={
                  userInfo ? <AssistantPage /> : <Navigate to="/login" replace />
                }
              />
            </Routes>
          </Col>
        </Row>
      </Container>
    </Router>
  );
}

export default App;