import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from 'react-markdown';
import "./ChatBot.css";

// Accept user and logout function as props
function ChatBot({ getToken, user, logout }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! I am your SOC Assistant. Ask me about IPs, malware, CVEs, etc." }
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);
    const currentInput = input;
    setInput("");

    try {
      const token = await getToken();
      if (!token) throw new Error("JWT token not found");

      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-token": token
        },
        body: JSON.stringify({ query: currentInput })
      });

      if (!response.ok) throw new Error(`Backend error: ${response.status}`);

      const data = await response.json();
      setMessages(prev => [...prev, { sender: "bot", text: data.result }]);
    } catch (err) {
      console.error("Error calling backend:", err);
      setMessages(prev => [...prev, { sender: "bot", text: "Sorry, I couldn't connect to the backend." }]);
    }
  };

  const handleKeyPress = e => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <span className="user-info">Logged in as {user.name}</span>
        <button onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>
          Logout
        </button>
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
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="input-area-wrapper">
        <div className="chat-content-wrapper">
          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your query..."
            />
            <button onClick={handleSend}>➤</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatBot;