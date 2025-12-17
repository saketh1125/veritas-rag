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
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "800px" }}>
      <h1>Veritas-RAG</h1>

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
