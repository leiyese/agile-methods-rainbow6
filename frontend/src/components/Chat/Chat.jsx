import { useState, useRef, useEffect } from "react";
import "./Chat.css";
import ChatInput from "./ChatInput";
import { askAssistant } from '../../api/assistantApi';
import Logo from "./Logo"

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

    try {
      const result = await askAssistant(message, false); // Set to true for mock mode
      
      if (result.success) {
        const assistantMessage = {
          type: "assistant",
          content: result.data.answer,
          metadata: {
            model: result.data.model_used,
            latency: result.data.latency_ms,
            traceId: result.data.trace_id
          }
        };
        
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage = {
          type: "assistant",
          content: `Ursäkta, det uppstod ett fel: ${result.error}`,
          isError: true
        };
        
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Unexpected error:', error);
      const errorMessage = {
        type: "assistant", 
        content: "Ursäkta, något gick fel. Försök igen senare.",
        isError: true
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <Logo />
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>
              Hej! Jag är din A-Z chatbot. Hur kan jag hjälpa dig idag?
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
      <ChatInput
        inputValue={inputValue}
        setInputValue={setInputValue}
        isLoading={isLoading}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}
