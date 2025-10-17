import { useEffect, useRef, useState } from "react";
import { askAssistant } from "../../api/assistantApi";
import "./Chat.css";
import ChatInput from "./ChatInput";
import Logo from "./Logo";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [expandedSources, setExpandedSources] = useState(new Set());
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const toggleSources = (index) => {
    setExpandedSources((prev) => {
      const s = new Set(prev);
      if (s.has(index)) s.delete(index);
      else s.add(index);
      return s;
    });
  };

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
          sources: result.data.sources || [],
          metadata: {
            model: result.data.model_used,
            latency: result.data.latency_ms,
            traceId: result.data.trace_id,
          },
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage = {
          type: "assistant",
          content: `Ursäkta, det uppstod ett fel: ${result.error}`,
          isError: true,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Unexpected error:", error);
      const errorMessage = {
        type: "assistant",
        content: "Ursäkta, något gick fel. Försök igen senare.",
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <Logo width={120} height={120} />
        <h2 className="chat-header-title">Hur kan jag hjälpa dig idag?</h2>
      </div>

      <div className="chat-messages">
        {messages.map((msg, index) => {
          const isExpanded = expandedSources.has(index);

          return (
            <div key={index} className={`message ${msg.type}`}>
              <div className="message-content">
                <strong className="sender">
                  {msg.type === "user" ? "Du" : "Assistent"}:
                </strong>
                <p>{msg.content}</p>

                {msg.sources &&
                  msg.sources.length > 0 &&
                  msg.type === "assistant" && (
                    <div className="sources-container">
                      <div className="sources-toggle-row">
                        <button
                          type="button"
                          className="sources-toggle"
                          aria-expanded={isExpanded}
                          onClick={() => toggleSources(index)}
                        >
                          {`Visa källor (${msg.sources.length})`}
                        </button>
                      </div>
                      
                      {isExpanded && (
                        <div className="sources-bubble">
                          <div className="sources-bubble-header">
                            <h4 className="sources-bubble-title">Källor ({msg.sources.length})</h4>
                            <button
                              type="button"
                              className="sources-bubble-close"
                              onClick={() => toggleSources(index)}
                              aria-label="Stäng källor"
                            >
                              ✕
                            </button>
                          </div>
                          <div className="sources-bubble-content">
                            {msg.sources.map((src, i) => (
                              <div key={i} className="source-item">
                                <a
                                  href={src.link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="source-link"
                                >
                                  {src.document}
                                </a>
                                {src.section && <span> — {src.section}</span>}
                                {src.excerpt && (
                                  <p className="excerpt">{src.excerpt}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
              </div>
            </div>
          );
        })}

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
