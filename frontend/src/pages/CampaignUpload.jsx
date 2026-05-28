import React, { useState, useRef } from "react";
import { UploadCloud, CheckCircle2, AlertTriangle, FileSpreadsheet, Download, RefreshCw, Eye } from "lucide-react";
import api from "../services/api";

export default function CampaignUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [parsedData, setParsedData] = useState([]);
  const [validationErrors, setValidationErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  
  const fileInputRef = useRef(null);

  // Drag handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  // Client-side CSV Parsing & Validation for immediate WOW feedback
  const processFile = (selectedFile) => {
    const isCsv = selectedFile.name.endsWith(".csv");
    if (!isCsv) {
      setErrorMsg("Please select a standard CSV (.csv) file.");
      setFile(null);
      setParsedData([]);
      return;
    }

    setFile(selectedFile);
    setErrorMsg("");
    setSuccessMsg("");
    setValidationErrors([]);

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      parseCSV(text);
    };
    reader.readAsText(selectedFile);
  };

  const parseCSV = (text) => {
    const lines = text.split(/\r?\n/);
    if (lines.length < 2) {
      setValidationErrors(["File seems to be empty or lacks data rows."]);
      return;
    }

    // Extract headers
    const headers = lines[0].split(",").map(h => h.trim().toLowerCase());
    const requiredHeaders = [
      "campaign_name", "platform", "spend", "clicks", 
      "impressions", "conversions", "device", 
      "audience_age", "geography", "hour", "date"
    ];

    const missing = requiredHeaders.filter(h => !headers.includes(h));
    if (missing.length > 0) {
      setValidationErrors([`Missing required headers: ${missing.join(", ")}`]);
      setParsedData([]);
      return;
    }

    const rows = [];
    const errors = [];
    
    // Parse first 10 rows for preview
    const maxPreviewRows = Math.min(lines.length, 11); // Header + 10 rows
    for (let i = 1; i < maxPreviewRows; i++) {
      if (!lines[i].trim()) continue;
      
      const values = lines[i].split(",").map(v => v.trim());
      if (values.length !== headers.length) {
        errors.push(`Row ${i + 1}: Column count mismatch (expected ${headers.length}, got ${values.length})`);
        continue;
      }

      const rowObj = {};
      headers.forEach((header, idx) => {
        rowObj[header] = values[idx];
      });

      // Basic local validation checks
      const spend = parseFloat(rowObj.spend);
      const clicks = parseInt(rowObj.clicks);
      const impressions = parseInt(rowObj.impressions);
      const conversions = parseInt(rowObj.conversions);
      const hour = parseInt(rowObj.hour);

      if (isNaN(spend) || spend < 0) errors.push(`Row ${i + 1}: spend must be a positive number.`);
      if (isNaN(clicks) || clicks < 0) errors.push(`Row ${i + 1}: clicks must be a positive integer.`);
      if (isNaN(impressions) || impressions < 0) errors.push(`Row ${i + 1}: impressions must be a positive integer.`);
      if (isNaN(conversions) || conversions < 0) errors.push(`Row ${i + 1}: conversions must be a positive integer.`);
      if (isNaN(hour) || hour < 0 || hour > 23) errors.push(`Row ${i + 1}: hour must be between 0 and 23.`);
      
      rows.push(rowObj);
    }

    setParsedData(rows);
    setValidationErrors(errors);
  };

  const handleUploadSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/api/campaigns/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setSuccessMsg(response.data.message + " The ML prediction models are currently retraining in the background.");
      // Reset State
      setFile(null);
      setParsedData([]);
      setValidationErrors([]);
    } catch (err) {
      console.error(err);
      setErrorMsg(
        err.response?.data?.detail || "An error occurred while uploading your campaigns."
      );
    } finally {
      setLoading(false);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="space-y-6 animate-fade-in" id="campaign-upload-view">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold font-outfit text-white tracking-tight">
          Campaign Data Upload
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload marketing metrics to calibrate analytics and prediction engines.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Upload Zone */}
        <div className="lg:col-span-2 space-y-6">
          <div 
            id="file-dropzone-container"
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`glass-panel p-8 rounded-3xl border-2 border-dashed flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 ${
              dragActive 
                ? "border-brand-indigo bg-indigo-500/5 shadow-inner" 
                : "border-slate-800/80 hover:border-slate-700"
            }`}
            onClick={triggerFileSelect}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="csv-file-input"
            />
            
            <div className="p-4 rounded-full bg-slate-800/40 text-brand-indigo mb-4 border border-slate-800 shadow-md">
              <UploadCloud size={32} />
            </div>

            <h3 className="text-lg font-bold font-outfit text-white mb-2">
              {file ? file.name : "Select your campaign file"}
            </h3>
            
            <p className="text-slate-400 text-xs max-w-sm mb-1">
              Drag and drop your marketing campaign CSV file here, or click to browse.
            </p>
            <p className="text-slate-500 text-[10px]">
              Supports standard CSV layout formatting. Max size 20MB.
            </p>
          </div>

          {/* Error and Success Alerts */}
          {errorMsg && (
            <div 
              id="upload-error-alert"
              className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-brand-rose text-sm font-medium flex items-center gap-2.5"
            >
              <AlertTriangle size={18} />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div 
              id="upload-success-alert"
              className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-brand-emerald text-sm font-medium flex items-center gap-2.5"
            >
              <CheckCircle2 size={18} />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Client-Side Validation Alert Console */}
          {validationErrors.length > 0 && (
            <div 
              id="upload-validation-warning-console"
              className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs font-medium space-y-1.5"
            >
              <h4 className="font-bold flex items-center gap-1.5 text-sm text-amber-300">
                <AlertTriangle size={16} />
                Validation Warnings ({validationErrors.length})
              </h4>
              <div className="max-h-24 overflow-y-auto pr-2 space-y-1 text-slate-300">
                {validationErrors.map((err, i) => (
                  <p key={i}>• {err}</p>
                ))}
              </div>
            </div>
          )}

          {/* Interactive Parsed Data Preview Panel */}
          {parsedData.length > 0 && (
            <div className="glass-panel p-6 rounded-3xl space-y-4" id="parsed-data-preview-panel">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-white font-bold font-outfit text-sm">
                  <Eye size={18} className="text-brand-cyan" />
                  <span>Data Preview (First 5 Rows)</span>
                </div>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-brand-cyan/15 text-brand-cyan">
                  Valid CSV Schema
                </span>
              </div>

              <div className="overflow-x-auto border border-slate-800/80 rounded-2xl">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-800/50 text-slate-400 border-b border-slate-800 font-semibold">
                      <th className="p-3">Campaign</th>
                      <th className="p-3">Platform</th>
                      <th className="p-3">Spend</th>
                      <th className="p-3">Clicks</th>
                      <th className="p-3">Impressions</th>
                      <th className="p-3">Conversions</th>
                      <th className="p-3">Platform Slice</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parsedData.slice(0, 5).map((row, index) => (
                      <tr key={index} className="border-b border-slate-800/40 text-slate-300 hover:bg-slate-800/20">
                        <td className="p-3 font-semibold text-white truncate max-w-[120px]">{row.campaign_name}</td>
                        <td className="p-3">{row.platform}</td>
                        <td className="p-3">${parseFloat(row.spend).toFixed(2)}</td>
                        <td className="p-3">{parseInt(row.clicks).toLocaleString()}</td>
                        <td className="p-3">{parseInt(row.impressions).toLocaleString()}</td>
                        <td className="p-3">{parseInt(row.conversions).toLocaleString()}</td>
                        <td className="p-3">
                          <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">
                            {row.device} • {row.geography}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <button
                id="btn-upload-submit"
                onClick={handleUploadSubmit}
                disabled={loading || validationErrors.length > 0}
                className="w-full glass-btn-primary py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Commit & Process Data</span>
                  </>
                )}
              </button>
            </div>
          )}

        </div>

        {/* Right Side: Setup Instructions */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl space-y-4" id="upload-instructions-panel">
            <h3 className="text-lg font-bold font-outfit text-white flex items-center gap-2">
              <FileSpreadsheet size={20} className="text-brand-indigo" />
              Template Setup
            </h3>
            
            <p className="text-slate-400 text-xs leading-relaxed">
              Your CSV file columns must match our schema exactly. Make sure column names are in lowercase, separated by commas.
            </p>

            <div className="p-4 rounded-2xl bg-slate-800/30 border border-slate-800/50 space-y-3">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Required Columns</h4>
              <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] text-slate-400">
                <div>• <code className="text-brand-indigo">campaign_name</code></div>
                <div>• <code className="text-brand-indigo">platform</code></div>
                <div>• <code className="text-brand-indigo">spend</code></div>
                <div>• <code className="text-brand-indigo">clicks</code></div>
                <div>• <code className="text-brand-indigo">impressions</code></div>
                <div>• <code className="text-brand-indigo">conversions</code></div>
                <div>• <code className="text-brand-indigo">device</code></div>
                <div>• <code className="text-brand-indigo">audience_age</code></div>
                <div>• <code className="text-brand-indigo">geography</code></div>
                <div>• <code className="text-brand-indigo">hour</code></div>
                <div>• <code className="text-brand-indigo">date</code></div>
              </div>
            </div>

            <a
              id="link-download-template"
              href="http://127.0.0.1:8000/api/campaigns/template"
              download
              className="w-full glass-btn-secondary py-2.5 rounded-xl text-xs flex items-center justify-center gap-2 hover:text-white"
            >
              <Download size={14} />
              <span>Download CSV Template</span>
            </a>
          </div>
        </div>

      </div>
    </div>
  );
}
