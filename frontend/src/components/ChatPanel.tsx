import { useEffect, useRef, useState } from "react";
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Form,
  InputGroup,
} from "react-bootstrap";
import { marked } from "marked";
import { sendChatMessage } from "../services/chatService";

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
    <div className="d-flex flex-column">
      <Card className="flex-grow-1 d-flex flex-column">
        <CardHeader>
          <CardTitle>Chat with Me!</CardTitle>
        </CardHeader>
        <CardBody className="d-flex flex-column p-0">
          {/* Scrollable message container */}
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

          {/* Fixed input */}
          <div className="p-3 border-top bg-white">
            <InputGroup>
              <Form.Control
                type="text"
                value={input}
                placeholder="Type your message..."
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
              />
              <Button onClick={send} variant="primary">
                Send
              </Button>
            </InputGroup>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}