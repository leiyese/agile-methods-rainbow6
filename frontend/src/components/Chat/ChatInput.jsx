import { useRef, useEffect } from "react";

export default function ChatInput({ 
  inputValue, 
  setInputValue, 
  isLoading, 
  onSendMessage 
}) {
  const inputRef = useRef(null);

  useEffect(() => {
    // Auto-focus on mount and when loading completes
    if (!isLoading && inputRef.current) {
      inputRef.current.focus({ preventScroll: true });
    }
  }, [isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSendMessage(inputValue);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSendMessage(inputValue);
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Skriv ditt meddelande här..."
          disabled={isLoading}
          className="chat-input"
          autoFocus
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          className="send-button"
        ></button>
      </div>
    </form>
  );
}