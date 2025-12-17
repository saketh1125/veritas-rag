import { useState } from "react";
import { queryRag } from "../api";

function Query() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await queryRag(question);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "3rem" }}>
      <h2>Ask a Question</h2>

      <textarea
        rows={3}
        style={{ width: "100%" }}
        placeholder="Ask something about the uploaded document..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <br /><br />

      <button onClick={handleQuery} disabled={loading}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          <h3>Answer</h3>
          <p>{result.answer}</p>

          <h4>Citations</h4>
          <ul>
            {result.citations.map((c, idx) => (
              <li key={idx}>
                Source {c.source}, Page {c.page}
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && <p style={{ color: "red" }}>Error: {error}</p>}
    </div>
  );
}

export default Query;
