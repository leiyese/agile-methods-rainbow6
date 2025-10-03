export default function ChatInput({ 
  inputValue, 
  setInputValue, 
  isLoading, 
  onSendMessage 
}) {
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
  );
}