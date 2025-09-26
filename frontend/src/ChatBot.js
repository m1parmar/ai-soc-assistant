import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from 'react-markdown';
import "./ChatBot.css";

const getInitials = (name) => {
  if (!name) return "?";
  const names = name.split(' ');
  const initials = names.map(n => n[0]).join('');
  return initials.slice(0, 2).toUpperCase();
};

function ChatBot({ getToken, user, logout, theme, toggleTheme }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! I am Cybrarian, your SOC Assistant. How can I help?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const abortControllerRef = useRef(null); // Ref for the AbortController

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    abortControllerRef.current = new AbortController();
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
        body: JSON.stringify({ query: currentInput }),
        signal: abortControllerRef.current.signal
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
      if (err.name === 'AbortError') {
        console.log('Fetch aborted by user.');
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          const updatedLastMessage = { ...lastMessage, text: lastMessage.text + "\n\n*(Generation stopped)*" };
          return [...prev.slice(0, -1), updatedLastMessage];
        });
      } else {
        console.error("Error calling backend:", err);
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          const updatedLastMessage = { ...lastMessage, text: "Sorry, I couldn't connect." };
          return [...prev.slice(0, -1), updatedLastMessage];
        });
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleStopGenerating = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const handleKeyPress = e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

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
              <div className="avatar">
                {msg.sender === 'bot' ? 'C' : getInitials(user.name)}
              </div>
              <div className="bubble">
                {msg.text ? <ReactMarkdown>{msg.text}</ReactMarkdown> : <div className="typing-indicator"><span></span><span></span><span></span></div>}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="input-area-wrapper">
        <div className="chat-content-wrapper">
          <div className="input-area">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your query..."
              disabled={isLoading}
              rows={1}
            />
            <button onClick={handleSend} disabled={!input.trim() || isLoading}>➤</button>
          </div>
          {isLoading && (
            <div className="stop-button-wrapper">
              <button onClick={handleStopGenerating} className="stop-button">
                ■ Stop Generating
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatBot;