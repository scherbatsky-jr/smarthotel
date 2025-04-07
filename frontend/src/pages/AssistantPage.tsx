import DashboardPanel from "../components/DashboardPanel";
import ChatPanel from "../components/ChatPanel";
import { Col, Container, Row } from "react-bootstrap";

export default function AssistantPage() {
  return (
    <Container fluid style={{ marginTop: "1rem" }}>
      <Row>
        <Col>
        <DashboardPanel />
        </Col>
      </Row>
      <Row className="mt-3 d-flex justify-content-center">
        <hr  className="m-1"/>
      </Row>
      <Row className="mt-3">
        <Col>
          <ChatPanel />
        </Col>
      </Row>
      <Row className="mt-3 d-flex justify-content-center">
        <hr  className="m-1"/>
      </Row>
    </Container>
  );
}