import { useEffect, useState } from "react";

import {
  listTransactions,
  uploadTransactionsCsv,
} from "../api/transactions";

import { formatCurrency } from "../utils/format";

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  async function loadTransactions() {
    try {
      setIsLoading(true);
      setError(null);

      const data = await listTransactions(0, 100);
      setTransactions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadTransactions();
  }, []);

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

      setUploadResult(result);

      await loadTransactions();

      setSelectedFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div
      style={{
        padding: "2.5rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 1250,
        margin: "0 auto",
      }}
    >
      <div style={{ marginBottom: "2rem" }}>
        <h1
          style={{
            margin: 0,
            marginBottom: "0.5rem",
            fontSize: "2.2rem",
          }}
        >
          Transactions
        </h1>

        <p style={{ margin: 0, opacity: 0.75 }}>
          Upload and view your financial transactions.
        </p>
      </div>

      {/* Upload Section */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Upload Transactions CSV</h3>

        <input
          type="file"
          accept=".csv"
          onChange={(e) => {
            setSelectedFile(e.target.files[0]);
            setUploadResult(null);
            setError(null);
          }}
        />

        <button
          onClick={handleUpload}
          disabled={isUploading}
          style={{
            marginLeft: "1rem",
            padding: "0.6rem 1rem",
            cursor: isUploading ? "not-allowed" : "pointer",
          }}
        >
          {isUploading ? "Uploading..." : "Upload CSV"}
        </button>
      </div>

      {/* Upload Result */}
      {uploadResult && (
        <div
          style={{
            marginBottom: "1.5rem",
            padding: "1rem",
            border: "1px solid #4ade80",
            borderRadius: 10,
          }}
        >
          <strong>Upload successful!</strong>

          <p>Rows received: {uploadResult.rows_received}</p>
          <p>Rows inserted: {uploadResult.rows_inserted}</p>
          <p>Duplicates skipped: {uploadResult.duplicates_skipped}</p>
          <p>Rows skipped: {uploadResult.rows_skipped}</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            marginBottom: "1.5rem",
            padding: "1rem",
            color: "red",
            border: "1px solid #fca5a5",
            borderRadius: 10,
          }}
        >
          Error: {error}
        </div>
      )}

      {/* Loading */}
      {isLoading ? (
  <div
    style={{
      border: "1px solid #ddd",
      borderRadius: 12,
      padding: "3rem 2rem",
      textAlign: "center",
    }}
  >
    <div
      style={{
        fontSize: "2.5rem",
        marginBottom: "1rem",
      }}
    >
      
    </div>

    <h2 style={{ marginBottom: "0.5rem" }}>
      Loading Transactions
    </h2>

    <p
      style={{
        margin: 0,
        opacity: 0.7,
      }}
    >
      Loading your transaction history...
    </p>
  </div>
) : (
        <>
          {/* Transaction Count */}
          <p style={{ marginBottom: "1rem" }}>
            Showing {transactions.length} transactions.
          </p>

          {/* Empty State */}
          {transactions.length === 0 ? (
            <div
              style={{
                border: "1px solid #ddd",
                borderRadius: 12,
                padding: "3rem 2rem",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: "3rem",
                  marginBottom: "1rem",
                }}
              >
                📄
              </div>

              <h2 style={{ marginBottom: "0.75rem" }}>
                No transactions yet
              </h2>

              <p
                style={{
                  maxWidth: 550,
                  margin: "0 auto 1.5rem",
                  lineHeight: 1.6,
                  opacity: 0.75,
                }}
              >
                Your transaction history is currently empty. Upload a
                transactions CSV file above to start analyzing your spending,
                income, savings, and financial behaviour.
              </p>

              <p
                style={{
                  margin: 0,
                  fontSize: "0.9rem",
                  opacity: 0.65,
                }}
              >
                Supported format: CSV
              </p>
            </div>
          ) : (
            /* Transaction Table */
            <div
              style={{
                overflowX: "auto",
                border: "1px solid #ddd",
                borderRadius: 12,
              }}
            >
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                }}
              >
                <thead>
                  <tr
                    style={{
                      textAlign: "left",
                      borderBottom: "1px solid #ddd",
                    }}
                  >
                    <th style={{ padding: "0.75rem" }}>Date</th>
                    <th style={{ padding: "0.75rem" }}>Description</th>
                    <th style={{ padding: "0.75rem" }}>Category</th>
                    <th style={{ padding: "0.75rem" }}>Amount</th>
                    <th style={{ padding: "0.75rem" }}>Type</th>
                    <th style={{ padding: "0.75rem" }}>Payment Mode</th>
                    <th style={{ padding: "0.75rem" }}>Recurring</th>
                  </tr>
                </thead>

                <tbody>
                  {transactions.map((t) => (
                    <tr
                      key={t.id}
                      style={{
                        borderBottom: "1px solid #eee",
                      }}
                    >
                      <td style={{ padding: "0.75rem" }}>
                        {t.txn_date}
                      </td>

                      <td style={{ padding: "0.75rem" }}>
                        {t.description}
                      </td>

                      <td style={{ padding: "0.75rem" }}>
                        {t.category || "—"}
                      </td>

                      <td style={{ padding: "0.75rem" }}>
                        {formatCurrency(t.amount)}
                      </td>

                      <td style={{ padding: "0.75rem" }}>
                        {t.txn_type}
                      </td>

                      <td style={{ padding: "0.75rem" }}>
                        {t.payment_mode || "—"}
                      </td>

                      <td style={{ padding: "0.75rem" }}>
                        {t.is_recurring ? "Yes" : "No"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Transactions;