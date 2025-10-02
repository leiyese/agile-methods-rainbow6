import { useState, useRef, useEffect } from "react";
import "./Chat.css";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    setMessages((prev) => [...prev, { type: "user", content: message }]);
    setInputValue("");
    setIsLoading(true);

    setTimeout(() => {
      const data = {
        type: "assistant",
        content: `Du frågade: "${message}". Detta är ett testsvar från assistenten.`,
      };
      setMessages((prev) => [...prev, data]);
      setIsLoading(false);
    }, 1000);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Rainbow6 Assistent</h2>
        <p>Fråga mig vad som helst för att komma igång!</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>
              Hej! Jag är din Rainbow6 assistent. Hur kan jag hjälpa dig idag?
            </p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="message-content">
              <strong className="sender">
                {msg.type === "user" ? "Du" : "Assistent"}:
              </strong>
              <p>{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="message-content">
              <strong className="sender">Assistent:</strong>
              <p>
                <span className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
                Tänker...
              </p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-container" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Skriv ditt meddelande här..."
            disabled={isLoading}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="send-button"
          ></button>
        </div>
      </form>
    </div>
  );
}
