import React from 'react';
import './LandingPage.css';

// The login function is passed down as a prop from App.js
function LandingPage({ login }) {
  return (
    <div className="landing-page">
      <nav className="navbar">
        <div className="navbar-brand">Cybrarian</div>
        <button className="login-button" onClick={login}>
          Login
        </button>
      </nav>

      <header className="hero-section">
        <h1>Your AI-Powered SOC Assistant</h1>
        <p>
          Cybrarian integrates with leading security tools to provide instant
          threat intelligence, right when you need it.
        </p>
        <button className="cta-button" onClick={login}>
          Get Started
        </button>
        
      </header>

      <section className="features-section">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Instant IP Analysis</h3>
            <p>
              Leverage real-time data from VirusTotal to assess the reputation of
              any IP address in seconds.
            </p>
          </div>
          <div className="feature-card">
            <h3>AI-Powered Insights</h3>
            <p>
              Go beyond raw data. Our AI provides clear, human-readable
              analysis and recommendations for security events.
            </p>
          </div>
          <div className="feature-card">
            <h3>Secure and Authenticated</h3>
            <p>
              Built with Auth0 to ensure that only authorized personnel can
              access sensitive security information.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;