import { useState } from "react";
import { Form, Button, Container, Alert } from "react-bootstrap";
import { loginWithPasskey } from "../services/authService";

export default function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [passkey, setPasskey] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    try {
      await loginWithPasskey(passkey);
      window.location.reload();
    } catch {
      setError("Invalid passkey. Please try again.");
    }
  };

  return (
    <Container className="p-4" style={{ maxWidth: 400 }}>
      <h3 className="text-center mb-4">Welcome</h3>
      {error && <Alert variant="danger">{error}</Alert>}

      <Form.Group className="mb-3">
        <Form.Label>Enter your passkey</Form.Label>
        <Form.Control
          type="text"
          value={passkey}
          onChange={(e) => setPasskey(e.target.value)}
          placeholder="e.g. A1B2C3"
        />
      </Form.Group>

      <Button className="w-100" onClick={handleLogin}>Login</Button>
    </Container>
  );
}
