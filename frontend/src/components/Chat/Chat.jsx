import { useEffect, useRef, useState } from "react";
import { askAssistant } from "../../api/assistantApi";
import "./Chat.css";
import ChatInput from "./ChatInput";
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

  // Close all sources when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Check if click is outside sources bubble
      if (!event.target.closest('.sources-container')) {
        setExpandedSources(new Set());
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleSources = (index) => {
    setExpandedSources((prev) => {
      const s = new Set(prev);
      if (s.has(index)) {
        // Close this bubble
        s.delete(index);
      } else {
        // Close all other bubbles and open this one
        s.clear();
        s.add(index);
      }
      return s;
    });
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Close any open sources bubbles
    setExpandedSources(new Set());
    
    setMessages((prev) => [...prev, { type: "user", content: message }]);
    setInputValue("");
    setIsLoading(true);

    try {
      const result = await askAssistant(message);

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
                            {msg.sources.map((src, i) => {
                              // Format page information
                              let pageInfo = '';
                              if (src.page_start && src.page_start > 0) {
                                if (src.page_end && src.page_end !== src.page_start) {
                                  pageInfo = `Sida ${src.page_start}-${src.page_end}`;
                                } else {
                                  pageInfo = `Sida ${src.page_start}`;
                                }
                              }
                              
                              return (
                                <div key={i} className="source-item">
                                  <div className="source-title">
                                    {src.link ? (
                                      <a
                                        href={src.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="source-link"
                                      >
                                        {src.document}
                                        <span className="external-link-icon">↗</span>
                                      </a>
                                    ) : (
                                      <span className="source-title-text">{src.document}</span>
                                    )}
                                  </div>
                                  <div className="source-metadata">
                                    {src.section_title && <span className="source-section-title">{src.section_title}</span>}
                                    {pageInfo && <span className="source-page-info">{pageInfo}</span>}
                                  </div>
                                </div>
                              );
                            })}
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
        onInputFocus={() => setExpandedSources(new Set())}
      />
    </div>
  );
}
