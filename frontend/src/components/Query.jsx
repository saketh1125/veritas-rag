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
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        marginTop: "3rem",
        padding: "1.5rem",
        border: "1px solid #ddd",
        borderRadius: "8px",
        background: "#fafafa",
      }}
    >
      <h2 style={{ marginBottom: "0.5rem" }}>Ask a Question</h2>
      <p style={{ color: "#555", marginTop: 0 }}>
        Ask questions grounded strictly in the uploaded document.
      </p>

      <textarea
        rows={3}
        style={{
          width: "100%",
          padding: "0.75rem",
          borderRadius: "6px",
          border: "1px solid #ccc",
          fontFamily: "inherit",
          resize: "vertical",
        }}
        placeholder="e.g. What is the title of the document?"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <button
        onClick={handleQuery}
        disabled={loading}
        style={{
          marginTop: "0.75rem",
          padding: "0.5rem 1rem",
          borderRadius: "6px",
          border: "none",
          background: "#111",
          color: "#fff",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Thinking…" : "Ask"}
      </button>

      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          <h3>Answer</h3>
          <p
            style={{
    background: "#fff",
    padding: "1rem",
    borderRadius: "6px",
    border: "1px solid #e0e0e0",
    color: "#111",
    fontSize: "0.95rem",
  }}
          >
            {result.answer}
          </p>

          <h4 style={{ marginTop: "1rem" }}>Citations</h4>
          <ul style={{ color: "#111", fontSize: "0.9rem" }}>
  {result.citations.map((c, idx) => (
    <li key={idx}>
      Source {c.source}, Page {c.page}
    </li>
  ))}
</ul>

        </div>
      )}

      {error && (
        <p style={{ color: "red", marginTop: "1rem" }}>
          Error: {error}
        </p>
      )}
    </div>
  );
}

export default Query;
