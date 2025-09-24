import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from 'react-markdown';
import "./ChatBot.css";

function ChatBot({ getToken, user, logout, theme, toggleTheme }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! I am your SOC Assistant. Ask me anything." }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const currentInput = input;
    setInput("");
    setIsLoading(true);

    setMessages(prev => [
      ...prev,
      { sender: "user", text: currentInput },
      { sender: "bot", text: "" }
    ]);

    try {
      const token = await getToken();
      const response = await fetch(`${BACKEND_URL}/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-token": token },
        body: JSON.stringify({ query: currentInput })
      });

      if (!response.body) throw new Error("Response body is null");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          const updatedLastMessage = { ...lastMessage, text: lastMessage.text + chunk };
          return [...prev.slice(0, -1), updatedLastMessage];
        });
      }

    } catch (err) {
      console.error("Error calling backend:", err);
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        const updatedLastMessage = { ...lastMessage, text: "Sorry, I couldn't connect." };
        return [...prev.slice(0, -1), updatedLastMessage];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = e => { if (e.key === "Enter") handleSend(); };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <span className="user-info">Logged in as {user.name}</span>
        <div>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
          </button>
          <button onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>
            Logout
          </button>
        </div>
      </div>

      <div className="messages-list">
        <div className="chat-content-wrapper">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}`}>
              <div className="bubble">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message bot">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="input-area-wrapper">
        <div className="chat-content-wrapper">
          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)} // <-- THIS IS THE CORRECTED LINE
              onKeyPress={handleKeyPress}
              placeholder="Type your query..."
              disabled={isLoading}
            />
            <button onClick={handleSend} disabled={isLoading}>➤</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatBot;