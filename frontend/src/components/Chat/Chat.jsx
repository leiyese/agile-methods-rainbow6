import { useState, useRef, useEffect } from "react";
import "./Chat.css";
import ChatInput from "./ChatInput";
import { askAssistant } from "../../api/assistantApi";
import Logo from "./Logo";
import { parseAnswer } from "../../api/response_handler";

export default function Chat() {
  const initialMessages = [
    {
      type: "assistant",
      content: "Ställ din fråga om olycksfallsförsäkringen",
      sources: [],
      metadata: {},
    },
  ];
  const [messages, setMessages] = useState(initialMessages);
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
      const result = await askAssistant(message, false);

      if (result.success) {
        const parsed = parseAnswer(result.data || result);

        const assistantMessage = {
          type: "assistant",
          content: parsed.answer || result.data?.answer || "",
          sources: parsed.sources || [],
          metadata: {
            model: result.data?.model_used || result.data?.model || null,
            latency: result.data?.latency_ms ?? null,
            traceId: result.data?.trace_id || null,
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
                    <>
                      <div className="sources-toggle-row">
                        <button
                          type="button"
                          className="sources-toggle"
                          aria-expanded={isExpanded}
                          onClick={() => toggleSources(index)}
                        >
                          {isExpanded
                            ? "Dölj källor"
                            : `Visa källor (${msg.sources.length})`}
                        </button>
                      </div>

                      <div
                        className={`sources ${
                          isExpanded ? "expanded" : "collapsed"
                        }`}
                      >
                        <h4 className="sources-title">Källor:</h4>

                        {msg.sources.map((src, i) => (
                          <div key={i} className="source-item">
                            <span className="source-link plain">
                              {src.document}
                            </span>
                            {src.section_title && (
                              <span> — {src.section_title}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </>
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
