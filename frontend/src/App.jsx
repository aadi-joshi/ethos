import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_BASE_URL = "http://127.0.0.1:8000";
const VIEW_UPLOAD = "upload";
const VIEW_DASHBOARD = "dashboard";
const VIEW_REPORT = "report";

function getBiasBadge(metricName, value) {
  if (metricName === "disparate_impact_ratio") {
    if (value >= 0.8) {
      return { label: "Low", tone: "low" };
    }
    if (value >= 0.6) {
      return { label: "Medium", tone: "medium" };
    }
    return { label: "High", tone: "high" };
  }

  if (value <= 0.1) {
    return { label: "Low", tone: "low" };
  }
  if (value <= 0.2) {
    return { label: "Medium", tone: "medium" };
  }
  return { label: "High", tone: "high" };
}

function App() {
  const [activeView, setActiveView] = useState(VIEW_UPLOAD);
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [reportSnapshot, setReportSnapshot] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [analysisError, setAnalysisError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [targetColumn, setTargetColumn] = useState("");
  const [sensitiveAttribute, setSensitiveAttribute] = useState("");
  const [groundTruthColumn, setGroundTruthColumn] = useState("");

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
    setAnalysisResult(null);
    setReportSnapshot(null);
    setErrorMessage("");
    setAnalysisError("");
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
    setAnalysisResult(null);
    setAnalysisError("");

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
      const detectedColumns = payload.columns ?? [];
      setTargetColumn(detectedColumns[0] ?? "");
      setSensitiveAttribute(detectedColumns[1] ?? detectedColumns[0] ?? "");
      setGroundTruthColumn("");
      setActiveView(VIEW_DASHBOARD);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const onAnalyze = async () => {
    if (!selectedFile || !targetColumn || !sensitiveAttribute) {
      setAnalysisError("Select target column and sensitive attribute to analyze bias.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError("");
    setAnalysisResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("target_column", targetColumn);
      formData.append("sensitive_attribute", sensitiveAttribute);
      if (groundTruthColumn) {
        formData.append("ground_truth_column", groundTruthColumn);
      }

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail ?? "Bias analysis failed.");
      }

      setAnalysisResult(payload);
      setReportSnapshot({
        summary: {
          risk_level: "pending",
          generated_at: new Date().toISOString(),
        },
        metrics: payload,
      });
    } catch (error) {
      setAnalysisError(error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const chartData = useMemo(() => {
    if (!analysisResult) {
      return [];
    }

    return Object.entries(analysisResult.group_metrics).map(([group, metrics]) => ({
      group,
      selectionRate: Number(metrics.selection_rate ?? 0),
      falsePositiveRate: Number(metrics.false_positive_rate ?? 0),
    }));
  }, [analysisResult]);

  const overallBiasChartData = useMemo(() => {
    if (!analysisResult) {
      return [];
    }

    return [
      {
        metric: "Demographic Parity Diff",
        value: Number(analysisResult.overall_bias.demographic_parity_difference ?? 0),
      },
      {
        metric: "Disparate Impact Ratio",
        value: Number(analysisResult.overall_bias.disparate_impact_ratio ?? 0),
      },
      {
        metric: "FPR Difference",
        value: Number(analysisResult.overall_bias.false_positive_rate_difference ?? 0),
      },
    ];
  }, [analysisResult]);

  return (
    <main className="page">
      <section className="card">
        <h1>Ethos AI</h1>
        <p className="subtext">Fairness audit workflow</p>

        <nav className="top-nav">
          <button
            type="button"
            className={activeView === VIEW_UPLOAD ? "tab tab-active" : "tab"}
            onClick={() => setActiveView(VIEW_UPLOAD)}
          >
            Upload Page
          </button>
          <button
            type="button"
            className={activeView === VIEW_DASHBOARD ? "tab tab-active" : "tab"}
            onClick={() => setActiveView(VIEW_DASHBOARD)}
            disabled={!result}
          >
            Dashboard Page
          </button>
          <button
            type="button"
            className={activeView === VIEW_REPORT ? "tab tab-active" : "tab"}
            onClick={() => setActiveView(VIEW_REPORT)}
            disabled={!analysisResult}
          >
            Report View
          </button>
        </nav>

        {activeView === VIEW_UPLOAD && (
          <section className="panel">
            <h2>Upload Dataset</h2>
            <form className="upload-form" onSubmit={onUpload}>
              <input type="file" accept=".csv" onChange={onFileChange} />
              <button type="submit" disabled={isLoading}>
                {isLoading ? "Uploading..." : "Upload CSV"}
              </button>
            </form>

            {errorMessage && <p className="error">{errorMessage}</p>}

            {result && (
              <>
                <p className="success-text">Dataset uploaded successfully.</p>
                <button type="button" onClick={() => setActiveView(VIEW_DASHBOARD)}>
                  Go to Dashboard
                </button>
              </>
            )}
          </section>
        )}

        {activeView === VIEW_DASHBOARD && result && (
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

            <section className="panel">
              <h2>Bias Analysis Inputs</h2>
              <div className="analysis-form">
                <label>
                  Target Column
                  <select
                    value={targetColumn}
                    onChange={(event) => setTargetColumn(event.target.value)}
                  >
                    {result.columns.map((column) => (
                      <option key={column} value={column}>
                        {column}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Sensitive Attribute
                  <select
                    value={sensitiveAttribute}
                    onChange={(event) => setSensitiveAttribute(event.target.value)}
                  >
                    {result.columns.map((column) => (
                      <option key={column} value={column}>
                        {column}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Ground Truth Column (optional)
                  <select
                    value={groundTruthColumn}
                    onChange={(event) => setGroundTruthColumn(event.target.value)}
                  >
                    <option value="">Use target column</option>
                    {result.columns.map((column) => (
                      <option key={column} value={column}>
                        {column}
                      </option>
                    ))}
                  </select>
                </label>

                <button type="button" onClick={onAnalyze} disabled={isAnalyzing}>
                  {isAnalyzing ? "Analyzing..." : "Analyze Bias"}
                </button>
              </div>
            </section>

            {analysisError && <p className="error">{analysisError}</p>}

            {analysisResult && (
              <section className="analysis-result">
                <h2>Bias Metrics</h2>

                <div className="badge-row">
                  {Object.entries(analysisResult.overall_bias).map(([metricName, value]) => {
                    const badge = getBiasBadge(metricName, Number(value));
                    return (
                      <div key={metricName} className="badge-card">
                        <p className="badge-title">{metricName}</p>
                        <div className={`badge badge-${badge.tone}`}>{badge.label}</div>
                      </div>
                    );
                  })}
                </div>

                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Group</th>
                        <th>Selection Rate</th>
                        <th>False Positive Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(analysisResult.group_metrics).map(
                        ([group, metrics]) => (
                          <tr key={group}>
                            <td>{group}</td>
                            <td>{Number(metrics.selection_rate).toFixed(3)}</td>
                            <td>{Number(metrics.false_positive_rate).toFixed(3)}</td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>

                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Demographic Parity Difference</th>
                        <th>Disparate Impact Ratio</th>
                        <th>False Positive Rate Difference</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>
                          {Number(
                            analysisResult.overall_bias.demographic_parity_difference
                          ).toFixed(3)}
                        </td>
                        <td>
                          {Number(
                            analysisResult.overall_bias.disparate_impact_ratio
                          ).toFixed(3)}
                        </td>
                        <td>
                          {Number(
                            analysisResult.overall_bias.false_positive_rate_difference
                          ).toFixed(3)}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <h3>Group Comparison Chart</h3>
                <div className="chart-box">
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="group" />
                      <YAxis domain={[0, 1]} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="selectionRate" name="Selection Rate" fill="#111827" />
                      <Bar
                        dataKey="falsePositiveRate"
                        name="False Positive Rate"
                        fill="#6b7280"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <h3>Overall Bias Metrics Chart</h3>
                <div className="chart-box">
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={overallBiasChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="metric" />
                      <YAxis domain={[0, 1]} />
                      <Tooltip />
                      <Bar dataKey="value" name="Metric Value" fill="#374151" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <h3>Flagged Issues</h3>
                {analysisResult.flagged_issues.length === 0 ? (
                  <p>No fairness issues flagged for current thresholds.</p>
                ) : (
                  <ul>
                    {analysisResult.flagged_issues.map((issue) => (
                      <li key={issue}>{issue}</li>
                    ))}
                  </ul>
                )}

                <button type="button" onClick={() => setActiveView(VIEW_REPORT)}>
                  Open Report View
                </button>
              </section>
            )}
          </section>
        )}

        {activeView === VIEW_REPORT && (
          <section className="panel">
            <h2>Report View</h2>
            {!reportSnapshot ? (
              <p>Run bias analysis from Dashboard to prepare report content.</p>
            ) : (
              <>
                <p>
                  Risk Level: <strong>{reportSnapshot.summary.risk_level}</strong>
                </p>
                <p>Generated At: {reportSnapshot.summary.generated_at}</p>
                <p>
                  Report is prepared from the latest analysis. Next step will connect this view
                  to backend report, explanation, and recommendation APIs.
                </p>
              </>
            )}
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
