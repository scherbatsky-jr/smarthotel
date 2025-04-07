import { useEffect, useRef, useState } from "react";
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Container,
  Form,
  InputGroup,
  Row,
  Col
} from "react-bootstrap";
import { marked } from "marked";
import { sendChatMessage } from "../services/chatService";
import { BsFillSendFill } from "react-icons/bs";

export default function ChatPanel() {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const send = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setInput("");

    const botReply = await sendChatMessage(userMessage);
    setMessages((prev) => [...prev, { sender: "bot", text: botReply }]);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Container>
      <Row>
        <div>Chat with our smart assistant!</div>
      </Row>
      <Row className="mt-1">
      <Card>
      <div className="flex-grow-1 overflow-auto p-3 bg-light" style={{ height: "20rem", overflowY: "scroll" }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`d-flex mb-2 ${
                  msg.sender === "user"
                    ? "justify-content-end"
                    : "justify-content-start"
                }`}
              >
                <div
                  className={`p-2 rounded ${
                    msg.sender === "user"
                      ? "bg-primary text-white"
                      : "bg-secondary text-white"
                  }`}
                  style={{ maxWidth: "70%" }}
                >
                  {msg.sender === "user" ? (
                    msg.text
                  ) : (
                    <div dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }} />
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <Row className="chat-input-box p-2">
            <Col xs={10}>
              <Form.Control
                type="text"
                value={input}
                placeholder="Type your message..."
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
              />
            </Col>
            <Col xs={2}>
              <Button onClick={send} variant="primary">
                <BsFillSendFill />
              </Button>
            </Col>
          </Row>
        </Card>
      </Row>
    </Container>
  )
}