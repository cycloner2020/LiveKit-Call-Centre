import { useState, useCallback } from "react";
import "./App.css";
import LiveKitModal from "./components/LiveKitModal";

function App() {
  const [showSupport, setShowSupport] = useState(false);
  const [token, setToken] = useState(null);
  const [name, setName] = useState("");
  const [isSubmittingName, setIsSubmittingName] = useState(true);

  const getToken = useCallback(async (userName) => {
    try {
      const response = await fetch(
        `/api/getToken?name=${encodeURIComponent(userName)}`
      );
      const token = await response.text();
      setToken(token);
      setIsSubmittingName(false);
    } catch (error) {
      console.error("Failed to get token:", error);
    }
  }, []);

  const handleSupportClick = () => {
    setShowSupport(true);
    setIsSubmittingName(true);
    setToken(null);
  };

  const handleNameSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      getToken(name);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">AutoZone</div>
      </header>

      <main>
        <section className="hero">
          <h1>Get the Right Parts. Right Now.</h1>
          <p>Free Next Day Delivery on Eligible Orders</p>
          <div className="search-bar">
            <input type="text" placeholder="Enter vehicle or part number..." />
            <button>Search</button>
          </div>
        </section>

        <button className="support-button" onClick={handleSupportClick}>
          Talk to an Agent
        </button>
      </main>

      {showSupport && (
        <LiveKitModal
          setShowSupport={setShowSupport}
          token={token}
          isSubmittingName={isSubmittingName}
          name={name}
          setName={setName}
          handleNameSubmit={handleNameSubmit}
        />
      )}
    </div>
  );
}

export default App;
