import { useState } from "react";
import { uploadPdf } from "../api";

function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await uploadPdf(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
  style={{
    marginTop: "2rem",
    padding: "1.5rem",
    border: "1px solid #ddd",
    borderRadius: "8px",
    background: "#fafafa",
  }}
>

      <h2 style={{ marginBottom: "0.5rem" }}>Upload Document</h2>
<p style={{ color: "#555", marginTop: 0 }}>
  Upload a PDF to index it for question answering.
</p>


      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button
  onClick={handleUpload}
  disabled={loading}
  style={{
    padding: "0.5rem 1rem",
    borderRadius: "6px",
    border: "none",
    background: "#111",
    color: "#fff",
    cursor: "pointer",
  }}
>
  {loading ? "Uploading…" : "Upload"}
</button>


      {result && (
        <pre style={{ marginTop: "1rem", background: "#f4f4f4", padding: "1rem" }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}

      {error && <p style={{ color: "red" }}>Error: {error}</p>}
    </div>
  );
}

export default Upload;
