const BACKEND_URL = "";

export async function healthCheck() {
  const res = await fetch(`${BACKEND_URL}/health`);
  if (!res.ok) {
    throw new Error("Backend not reachable");
  }
  return res.json();
}
export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("http://127.0.0.1:8000/upload", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Upload failed");
  }

  return res.json();
}
export async function queryRag(question) {
  const res = await fetch("http://127.0.0.1:8000/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error("Query failed");
  }

  return res.json();
}
