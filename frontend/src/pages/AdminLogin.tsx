import { useState } from "react";
import { Form, Button, Container, Alert } from "react-bootstrap";
import { loginAsAdmin } from "../services/authService";

export default function AdminLoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await loginAsAdmin(username, password);
      window.location.reload();
    } catch (err) {
      setError("Invalid credentials or server error.");
    }
  };

  return (
    <Container className="d-flex justify-content-center align-items-center" style={{ height: "100vh" }}>
      <Form onSubmit={handleSubmit} className="p-4 shadow-sm border rounded" style={{ minWidth: "300px" }}>
        <h4 className="mb-4 text-center">Admin Login</h4>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form.Group className="mb-3">
          <Form.Label>Username</Form.Label>
          <Form.Control value={username} onChange={(e) => setUsername(e.target.value)} required />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Password</Form.Label>
          <Form.Control type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </Form.Group>
        <Button type="submit" variant="secondary" className="w-100">Login</Button>
      </Form>
    </Container>
  );
}
