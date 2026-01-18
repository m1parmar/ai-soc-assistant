import React, { useState, useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import ChatBot from "./ChatBot";
import LandingPage from "./LandingPage"; // Import the new component
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
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  if (isLoading) {
    return (
      <div className="app-container">
        <div className="loading-screen" role="status" aria-label="Loading application">
          <div className="loading-spinner" aria-hidden="true"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {!isAuthenticated ? (
        // Show the LandingPage if the user is not logged in
        <LandingPage login={loginWithRedirect} />
      ) : (
        // Show the ChatBot if the user is logged in
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