import React, { useState, useEffect, useRef, useCallback, useId } from "react";
import ReactMarkdown from 'react-markdown';
import "./ChatBot.css";

const getInitials = (name) => {
  if (!name) return "?";
  const names = name.split(' ');
  const initials = names.map(n => n[0]).join('');
  return initials.slice(0, 2).toUpperCase();
};

// Generate unique message ID
let messageIdCounter = 0;
const generateMessageId = () => `msg-${Date.now()}-${++messageIdCounter}`;

function ChatBot({ getToken, user, logout, theme, toggleTheme }) {
  const [messages, setMessages] = useState(() => [
    { id: generateMessageId(), sender: "bot", text: "Hello! I am Cybrarian, your SOC Assistant. How can I help?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Generate unique IDs for accessibility
  const inputId = useId();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    abortControllerRef.current = new AbortController();
    const currentInput = input;
    const userMessageId = generateMessageId();
    const botMessageId = generateMessageId();

    setInput("");
    setIsLoading(true);

    setMessages(prev => [
      ...prev,
      { id: userMessageId, sender: "user", text: currentInput },
      { id: botMessageId, sender: "bot", text: "" }
    ]);

    try {
      const token = await getToken();
      const response = await fetch(`${BACKEND_URL}/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-token": token },
        body: JSON.stringify({ query: currentInput }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      if (!response.body) throw new Error("Response body is null");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });

        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          return [...prev.slice(0, -1), { ...lastMessage, text: lastMessage.text + chunk }];
        });
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          return [...prev.slice(0, -1), { ...lastMessage, text: lastMessage.text + "\n\n*(Generation stopped)*" }];
        });
      } else {
        console.error("Error calling backend:", err);
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          return [...prev.slice(0, -1), { ...lastMessage, text: "Sorry, I couldn't connect. Please try again." }];
        });
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [input, isLoading, getToken, BACKEND_URL]);

  const handleStopGenerating = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const handleKeyPress = useCallback((e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  return (
    <div className="chatbot-container">
      <header className="chatbot-header">
        <span className="user-info">Logged in as {user.name}</span>
        <div className="header-actions">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
          </button>
          <button
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            aria-label="Log out of your account"
          >
            Logout
          </button>
        </div>
      </header>

      <main
        className="messages-list"
        role="log"
        aria-live="polite"
        aria-label="Chat messages"
      >
        <div className="chat-content-wrapper">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`message ${msg.sender}`}
              role="article"
              aria-label={`${msg.sender === 'bot' ? 'Cybrarian' : 'You'} said`}
            >
              <div className="avatar" aria-hidden="true">
                {msg.sender === 'bot' ? 'C' : getInitials(user.name)}
              </div>
              <div className="bubble">
                {msg.text ? (
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                ) : (
                  <div className="typing-indicator" role="status" aria-label="Cybrarian is typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <div className="input-area-wrapper">
        <div className="chat-content-wrapper">
          <label htmlFor={inputId} className="visually-hidden">
            Enter your security query
          </label>
          <div className="input-area">
            <textarea
              id={inputId}
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your query..."
              disabled={isLoading}
              rows={1}
              autoComplete="off"
              spellCheck="true"
              aria-describedby={isLoading ? "loading-status" : undefined}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              aria-label="Send message"
              type="button"
            >
              <span aria-hidden="true">&#10148;</span>
            </button>
          </div>
          {isLoading && (
            <div className="stop-button-wrapper">
              <span id="loading-status" className="visually-hidden">
                Generating response...
              </span>
              <button
                onClick={handleStopGenerating}
                className="stop-button"
                type="button"
                aria-label="Stop generating response"
              >
                <span aria-hidden="true">&#9632;</span> Stop Generating
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatBot;