import React from "react";
import { useAuth0 } from "@auth0/auth0-react";
import ChatBot from "./ChatBot";
import "./App.css"; // Import the new App CSS

function App() {
  const { 
    loginWithRedirect, 
    logout, 
    isAuthenticated, 
    getAccessTokenSilently, 
    user, 
    isLoading 
  } = useAuth0();

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
        />
      )}
    </div>
  );
}

export default App;