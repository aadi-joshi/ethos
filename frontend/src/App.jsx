import { useMemo, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const previewHeaders = useMemo(() => {
    if (!result || result.preview_rows.length === 0) {
      return [];
    }

    return Object.keys(result.preview_rows[0]);
  }, [result]);

  const onFileChange = (event) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setResult(null);
    setErrorMessage("");
  };

  const onUpload = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setErrorMessage("Please select a CSV file before uploading.");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail ?? "Upload failed.");
      }

      setResult(payload);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="page">
      <section className="card">
        <h1>Ethos AI</h1>
        <p className="subtext">Upload dataset for fairness analysis</p>

        <form className="upload-form" onSubmit={onUpload}>
          <input type="file" accept=".csv" onChange={onFileChange} />
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Uploading..." : "Upload CSV"}
          </button>
        </form>

        {errorMessage && <p className="error">{errorMessage}</p>}

        {result && (
          <section className="result">
            <h2>Dataset Summary</h2>

            <div className="summary-grid">
              <div>
                <strong>Rows</strong>
                <p>{result.basic_stats.row_count}</p>
              </div>
              <div>
                <strong>Columns</strong>
                <p>{result.basic_stats.column_count}</p>
              </div>
            </div>

            <h3>Column Names</h3>
            <ul>
              {result.columns.map((column) => (
                <li key={column}>{column}</li>
              ))}
            </ul>

            <h3>Preview (first 5 rows)</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    {previewHeaders.map((header) => (
                      <th key={header}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.preview_rows.map((row, rowIndex) => (
                    <tr key={`${rowIndex}-${previewHeaders.join("-")}`}>
                      {previewHeaders.map((header) => (
                        <td key={`${rowIndex}-${header}`}>{String(row[header])}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
