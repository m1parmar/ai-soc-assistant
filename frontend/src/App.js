import React, { useState, useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import ChatBot from "./ChatBot";
import "./App.css";

function App() {
  const { 
    loginWithRedirect, 
    logout, 
    isAuthenticated, 
    getAccessTokenSilently, 
    user, 
    isLoading 
  } = useAuth0();
  
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    // This line sets the data-theme attribute on the <html> tag
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="app-container">
      {!isAuthenticated ? (
        <div className="login-container">
          <button onClick={() => loginWithRedirect()}>Login</button>
        </div>
      ) : (
        <ChatBot 
          getToken={getAccessTokenSilently} 
          user={user} 
          logout={logout}
          theme={theme}
          toggleTheme={toggleTheme}
        />
      )}
    </div>
  );
}

export default App;