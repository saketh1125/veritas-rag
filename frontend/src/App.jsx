import { useEffect, useState } from "react";
import { healthCheck } from "./api";
import Upload from "./components/Upload";
import Query from "./components/Query";

function App() {
  const [status, setStatus] = useState("Checking backend...");
  const [error, setError] = useState(null);

  useEffect(() => {
    healthCheck()
      .then((data) => setStatus(`Backend status: ${data.status}`))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div
  style={{
    padding: "2rem",
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
    maxWidth: "900px",
    margin: "0 auto",
    lineHeight: 1.6,
  }}
    >

      <h1>Veritas-RAG</h1>
      <p style={{ color: "#666", marginTop: "-0.5rem" }}>
  A citation-aware Retrieval-Augmented Generation system
</p>


      {error ? (
        <p style={{ color: "red" }}>Error: {error}</p>
      ) : (
        <p>{status}</p>
      )}

      <Upload />
      <Query />
    </div>
  );
}

export default App;
