import React, { useCallback } from 'react';
import './LandingPage.css';

// The login function is passed down as a prop from App.js
function LandingPage({ login }) {
  const handleLogin = useCallback(() => {
    login();
  }, [login]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      login();
    }
  }, [login]);

  return (
    <div className="landing-page">
      <nav className="navbar" role="navigation" aria-label="Main navigation">
        <div className="navbar-brand" role="banner">Cybrarian</div>
        <button
          className="login-button"
          onClick={handleLogin}
          type="button"
          aria-label="Log in to Cybrarian"
        >
          Login
        </button>
      </nav>

      <header className="hero-section">
        <h1>Your AI-Powered SOC Assistant</h1>
        <p>
          Cybrarian integrates with leading security tools to provide instant
          threat intelligence, right when you need it.
        </p>
        <button
          className="cta-button"
          onClick={handleLogin}
          type="button"
          aria-label="Get started with Cybrarian"
        >
          Get Started
        </button>
      </header>

      <main>
        <section className="features-section" aria-labelledby="features-heading">
          <h2 id="features-heading">Features</h2>
          <div className="features-grid" role="list">
            <article className="feature-card" role="listitem">
              <h3>Instant IP Analysis</h3>
              <p>
                Leverage real-time data from VirusTotal to assess the reputation of
                any IP address in seconds.
              </p>
            </article>
            <article className="feature-card" role="listitem">
              <h3>AI-Powered Insights</h3>
              <p>
                Go beyond raw data. Our AI provides clear, human-readable
                analysis and recommendations for security events.
              </p>
            </article>
            <article className="feature-card" role="listitem">
              <h3>Secure and Authenticated</h3>
              <p>
                Built with Auth0 to ensure that only authorized personnel can
                access sensitive security information.
              </p>
            </article>
          </div>
        </section>
      </main>
    </div>
  );
}

export default LandingPage;