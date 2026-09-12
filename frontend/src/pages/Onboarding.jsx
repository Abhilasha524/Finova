import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useFile } from "../context/FileContext";
import { uploadTransactionsCsv } from "../api/transactions";

function Onboarding() {
  const navigate = useNavigate();

  const {
    selectedFile,
    setSelectedFile,
    setUploadResult,
  } = useFile();

  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  async function handleUpload() {
    if (!selectedFile) {
      setError("Please select a CSV file first.");
      return;
    }

    try {
      setIsUploading(true);
      setError(null);
      setUploadResult(null);

      const result = await uploadTransactionsCsv(selectedFile);

      const uploadTime = new Date().toISOString();
      localStorage.setItem("finova_last_upload", uploadTime);

      setUploadResult(result);
      setSelectedFile(null);

      window.location.href = "/";
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "calc(100vh - 80px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "3rem 2rem",
        fontFamily: "sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 850,
          border: "1px solid #ddd",
          borderRadius: 16,
          padding: "3rem",
          textAlign: "center",
        }}
      >
        <h1 style={{ marginTop: 0, marginBottom: "0.75rem" }}>
          Welcome to Finova
        </h1>

        <p
          style={{
            maxWidth: 650,
            margin: "0 auto 2rem",
            lineHeight: 1.6,
            opacity: 0.75,
          }}
        >
          Let's get your financial dashboard ready. Upload your transaction
          statement and Finova will analyze your income, expenses, savings and
          spending behaviour.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "1rem",
            marginBottom: "2rem",
            textAlign: "left",
          }}
        >
          <div
            style={{
              border: "1px solid #eee",
              borderRadius: 10,
              padding: "1rem",
            }}
          >
            <strong>1. Upload</strong>
            <p style={{ margin: "0.5rem 0 0", opacity: 0.7 }}>
              Import your transaction CSV.
            </p>
          </div>

          <div
            style={{
              border: "1px solid #eee",
              borderRadius: 10,
              padding: "1rem",
            }}
          >
            <strong>2. Analyze</strong>
            <p style={{ margin: "0.5rem 0 0", opacity: 0.7 }}>
              Finova processes your financial data.
            </p>
          </div>

          <div
            style={{
              border: "1px solid #eee",
              borderRadius: 10,
              padding: "1rem",
            }}
          >
            <strong>3. Understand</strong>
            <p style={{ margin: "0.5rem 0 0", opacity: 0.7 }}>
              Explore your personalized dashboard.
            </p>
          </div>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => {
              setSelectedFile(e.target.files[0]);
              setUploadResult(null);
              setError(null);
            }}
          />
        </div>

        {selectedFile && (
          <p style={{ margin: "0.75rem 0", opacity: 0.75 }}>
            Selected file: {selectedFile.name}
          </p>
        )}

        {error && (
          <p style={{ color: "#ef4444", margin: "1rem 0" }}>
            Error: {error}
          </p>
        )}

        <button
          onClick={handleUpload}
          disabled={isUploading}
          style={{
            marginTop: "0.75rem",
            padding: "0.75rem 1.5rem",
            border: "none",
            borderRadius: 8,
            background: "#324635",
            color: "white",
            fontSize: "1rem",
            cursor: isUploading ? "not-allowed" : "pointer",
          }}
        >
          {isUploading ? "Processing..." : "Upload & Continue"}
        </button>

        <p
          style={{
            marginTop: "1rem",
            marginBottom: 0,
            fontSize: "0.85rem",
            opacity: 0.6,
          }}
        >
          Finova currently supports CSV statement uploads.
        </p>
      </div>
    </div>
  );
}

export default Onboarding;
