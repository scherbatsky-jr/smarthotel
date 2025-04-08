import { Button, Container, Row, Col, Card } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <Container className="d-flex justify-content-center align-items-center" style={{ height: "100vh" }}>
      <Card className="p-4 shadow" style={{ minWidth: "300px" }}>
        <h4 className="mb-4 text-center">Select Your Role</h4>
        <Row className="mb-3">
          <Col>
            <Button variant="primary" className="w-100" onClick={() => navigate("/login/guest")}>
              Guest
            </Button>
          </Col>
        </Row>
        <Row>
          <Col>
            <Button variant="secondary" className="w-100" onClick={() => navigate("/login/admin")}>
              Admin
            </Button>
          </Col>
        </Row>
      </Card>
    </Container>
  );
}