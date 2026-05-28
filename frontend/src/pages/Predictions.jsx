import React, { useEffect, useState } from "react";
import { 
  BrainCircuit, 
  Play, 
  HelpCircle, 
  TrendingUp, 
  MousePointerClick, 
  Activity, 
  History, 
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  DollarSign
} from "lucide-react";
import api from "../services/api";

export default function Predictions() {
  // Form State
  const [campaignName, setCampaignName] = useState("");
  const [platform, setPlatform] = useState("Facebook");
  const [spend, setSpend] = useState(250);
  const [device, setDevice] = useState("Mobile");
  const [audienceAge, setAudienceAge] = useState("25-34");
  const [geography, setGeography] = useState("US");
  const [hour, setHour] = useState(19);

  // Result State
  const [result, setResult] = useState(null);
  const [simulating, setSimulating] = useState(false);
  
  // History & Recommendations State
  const [history, setHistory] = useState([]);
  const [generalRecs, setGeneralRecs] = useState(null);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [error, setError] = useState("");

  const fetchHistoryAndRecommendations = async () => {
    try {
      const [histRes, recsRes] = await Promise.all([
        api.get("/api/predict/history"),
        api.get("/api/predict/recommendations")
      ]);
      setHistory(histRes.data);
      setGeneralRecs(recsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingRecs(false);
    }
  };

  useEffect(() => {
    fetchHistoryAndRecommendations();
  }, []);

  const handleSimulate = async (e) => {
    e.preventDefault();
    setSimulating(true);
    setError("");

    try {
      const response = await api.post("/api/predict/", {
        campaign_name: campaignName || "Simulation Run",
        platform,
        spend: parseFloat(spend),
        device,
        audience_age: audienceAge,
        geography,
        hour: parseInt(hour)
      });
      
      setResult(response.data);
      // Reload history
      const histRes = await api.get("/api/predict/history");
      setHistory(histRes.data);
    } catch (err) {
      console.error(err);
      setError("Prediction failed. Make sure you have campaign records loaded.");
    } finally {
      setSimulating(false);
    }
  };

  const loadHistoryItem = (item) => {
    setCampaignName(item.campaign_name || "");
    setPlatform(item.platform);
    setSpend(item.spend);
    setDevice(item.device);
    setAudienceAge(item.audience_age);
    setGeography(item.geography);
    setHour(item.hour);
    setResult(item);
  };

  // SVG Gauge calculations
  const gaugeRadius = 45;
  const gaugeCircumference = 2 * Math.PI * gaugeRadius;
  const activeScore = result?.success_score || 0;
  const gaugeOffset = gaugeCircumference - (activeScore / 100) * gaugeCircumference;

  // Formatting hours to readable AM/PM
  const formatHour = (h) => {
    return `${h % 12 || 12}:00 ${h >= 12 ? "PM" : "AM"}`;
  };

  const getTips = (tipsJson) => {
    if (!tipsJson) return ["Optimized setup configuration."];
    try {
      return JSON.parse(tipsJson);
    } catch (e) {
      return [tipsJson];
    }
  };

  return (
    <div className="space-y-6 animate-fade-in" id="predictions-view">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold font-outfit text-white tracking-tight">
          Predict Success
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Simulate marketing configurations using Random Forest regressors to estimate ROI and click metrics.
        </p>
      </div>

      {error && (
        <div 
          id="prediction-error-alert"
          className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-brand-rose text-sm font-medium"
        >
          {error}
        </div>
      )}

      {/* Main Simulation Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Form Console */}
        <div className="glass-panel p-6 rounded-3xl" id="simulation-form-panel">
          <h3 className="text-lg font-bold font-outfit text-white mb-6 flex items-center gap-2">
            <BrainCircuit size={20} className="text-brand-indigo" />
            Simulation Console
          </h3>

          <form onSubmit={handleSimulate} className="space-y-4" id="prediction-form">
            <div>
              <label htmlFor="sim-campaign-name" className="block text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                Simulated Campaign Name
              </label>
              <input
                id="sim-campaign-name"
                type="text"
                placeholder="e.g. Q3_Mobile_Promo"
                value={campaignName}
                onChange={(e) => setCampaignName(e.target.value)}
                className="glass-input w-full px-4 py-2.5 rounded-xl text-sm"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="sim-platform" className="block text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  Platform
                </label>
                <select
                  id="sim-platform"
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 rounded-xl text-sm"
                >
                  {["Facebook", "Google Ads", "Instagram", "TikTok", "YouTube"].map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="sim-spend" className="block text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  Daily Budget ($)
                </label>
                <input
                  id="sim-spend"
                  type="number"
                  min="1"
                  value={spend}
                  onChange={(e) => setSpend(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 rounded-xl text-sm"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="sim-device" className="block text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  Device
                </label>
                <select
                  id="sim-device"
                  value={device}
                  onChange={(e) => setDevice(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 rounded-xl text-sm"
                >
                  {["Mobile", "Desktop", "Tablet"].map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="sim-age" className="block text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  Audience Age
                </label>
                <select
                  id="sim-age"
                  value={audienceAge}
                  onChange={(e) => setAudienceAge(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 rounded-xl text-sm"
                >
                  {["18-24", "25-34", "35-44", "45-54", "55+"].map(a => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="sim-geo" className="block text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  Geography
                </label>
                <select
                  id="sim-geo"
                  value={geography}
                  onChange={(e) => setGeography(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 rounded-xl text-sm"
                >
                  {["US", "UK", "CA", "AU", "DE"].map(g => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="sim-hour" className="block text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  Time of Day
                </label>
                <select
                  id="sim-hour"
                  value={hour}
                  onChange={(e) => setHour(e.target.value)}
                  className="glass-input w-full px-4 py-2.5 rounded-xl text-sm"
                >
                  {[...Array(24)].map((_, i) => (
                    <option key={i} value={i}>{formatHour(i)}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              id="btn-run-simulation"
              type="submit"
              disabled={simulating}
              className="w-full glass-btn-primary py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 mt-6 disabled:opacity-60"
            >
              {simulating ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Play size={16} fill="white" />
                  <span>Run Campaign Simulation</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Prediction Results Display */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 rounded-3xl min-h-[360px] flex flex-col justify-between" id="simulation-output-panel">
            
            {result ? (
              <div className="space-y-6" id="simulation-results-content">
                
                {/* Result Title */}
                <div className="flex justify-between items-start border-b border-slate-800/60 pb-4">
                  <div>
                    <h4 className="text-base font-bold text-white font-outfit">{result.campaign_name}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {result.platform} • ${result.spend} • {result.device} • {result.audience_age} • {result.geography} • {formatHour(result.hour)}
                    </p>
                  </div>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-brand-cyan/15 text-brand-cyan">
                    RF Calibration Active
                  </span>
                </div>

                {/* Score and Core Metrics */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-center">
                  
                  {/* Custom SVG Gauge */}
                  <div className="flex flex-col items-center justify-center text-center">
                    <div className="relative w-32 h-32 flex items-center justify-center">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r={gaugeRadius}
                          className="stroke-slate-800"
                          strokeWidth="8"
                          fill="transparent"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r={gaugeRadius}
                          className="stroke-brand-indigo transition-all duration-1000 ease-out"
                          strokeWidth="8"
                          fill="transparent"
                          strokeDasharray={gaugeCircumference}
                          strokeDashoffset={gaugeOffset}
                          strokeLinecap="round"
                        />
                      </svg>
                      <div className="absolute flex flex-col items-center">
                        <span className="text-3xl font-extrabold font-outfit text-white">{result.success_score}</span>
                        <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Success</span>
                      </div>
                    </div>
                    <span className="text-xs text-slate-400 font-medium mt-1">Campaign Success Score</span>
                  </div>

                  {/* Estimated Output Metrics */}
                  <div className="sm:col-span-2 grid grid-cols-3 gap-4">
                    <div className="bg-slate-800/30 border border-slate-800 p-4 rounded-2xl text-center">
                      <div className="flex justify-center text-brand-indigo mb-2"><MousePointerClick size={16} /></div>
                      <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Exp CTR</span>
                      <p className="text-lg font-bold font-outfit text-white mt-1">{result.expected_conversion_rate}%</p>
                    </div>
                    <div className="bg-slate-800/30 border border-slate-800 p-4 rounded-2xl text-center">
                      <div className="flex justify-center text-brand-cyan mb-2"><Activity size={16} /></div>
                      <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Exp CVR</span>
                      <p className="text-lg font-bold font-outfit text-white mt-1">{result.expected_conversion_rate}%</p>
                    </div>
                    <div className="bg-slate-800/30 border border-slate-800 p-4 rounded-2xl text-center">
                      <div className="flex justify-center text-brand-emerald mb-2"><TrendingUp size={16} /></div>
                      <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Exp ROI</span>
                      <p className="text-lg font-bold font-outfit text-white mt-1">{result.predicted_roi}%</p>
                    </div>
                  </div>

                </div>

                {/* AI Tuning Advice */}
                <div className="bg-slate-800/30 border border-slate-800/60 p-4 rounded-2xl space-y-3">
                  <h5 className="text-xs font-bold text-brand-cyan uppercase tracking-wider flex items-center gap-1.5">
                    <Lightbulb size={14} />
                    Simulation Recommendations
                  </h5>
                  <div className="space-y-2 text-xs text-slate-300">
                    {getTips(result.recommendations).map((tip, i) => (
                      <div key={i} className="flex gap-2.5 items-start">
                        {tip.includes("Ready") || tip.includes("aligns") ? (
                          <CheckCircle size={14} className="text-brand-emerald mt-0.5 shrink-0" />
                        ) : (
                          <AlertTriangle size={14} className="text-brand-rose mt-0.5 shrink-0" />
                        )}
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
                <HelpCircle size={48} className="text-slate-700 mb-4" />
                <h4 className="text-base font-bold text-slate-300 font-outfit">Console Awaiting Simulation</h4>
                <p className="text-xs text-slate-500 max-w-sm mt-1">
                  Adjust metrics on the left console and click execute. MarketPulse AI will score parameters against historical campaign models.
                </p>
              </div>
            )}

          </div>
        </div>

      </div>

      {/* Bottom Segment: Recommendations and History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* General Account Recommendations */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl" id="general-ai-recommendations-panel">
          <h3 className="text-lg font-bold font-outfit text-white mb-6 flex items-center gap-2">
            <Lightbulb size={20} className="text-brand-cyan animate-pulse" />
            AI Recommendations & Optimizations
          </h3>

          {loadingRecs ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-10 bg-slate-800/40 rounded-xl animate-shimmer" />
              ))}
            </div>
          ) : (
            <div className="space-y-6" id="ai-recs-content">
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Budget Tips */}
                <div className="p-4 rounded-2xl bg-slate-800/30 border border-slate-800/80 space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <DollarSign size={14} className="text-brand-indigo" />
                    Budget Allocations
                  </h4>
                  <div className="text-xs text-slate-400 leading-relaxed space-y-2">
                    {generalRecs?.budget_allocation.map((rec, i) => (
                      <p key={i} dangerouslySetInnerHTML={{ __html: rec }} />
                    ))}
                  </div>
                </div>

                {/* Timing Tips */}
                <div className="p-4 rounded-2xl bg-slate-800/30 border border-slate-800/80 space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Clock size={14} className="text-brand-violet" />
                    Time Scheduling
                  </h4>
                  <div className="text-xs text-slate-400 leading-relaxed space-y-2">
                    {generalRecs?.timing_optimization.map((rec, i) => (
                      <p key={i} dangerouslySetInnerHTML={{ __html: rec }} />
                    ))}
                  </div>
                </div>

                {/* Demographic Tips */}
                <div className="p-4 rounded-2xl bg-slate-800/30 border border-slate-800/80 space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Users size={14} className="text-brand-cyan" />
                    Demographics & Devices
                  </h4>
                  <div className="text-xs text-slate-400 leading-relaxed space-y-2">
                    {generalRecs?.demographic_insights.map((rec, i) => (
                      <p key={i} dangerouslySetInnerHTML={{ __html: rec }} />
                    ))}
                  </div>
                </div>

                {/* Ad creative & Funnel Tips */}
                <div className="p-4 rounded-2xl bg-slate-800/30 border border-slate-800/80 space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <TrendingUp size={14} className="text-brand-emerald" />
                    Creative & Funnels
                  </h4>
                  <div className="text-xs text-slate-400 leading-relaxed space-y-2">
                    {generalRecs?.ad_performance.map((rec, i) => (
                      <p key={i} dangerouslySetInnerHTML={{ __html: rec }} />
                    ))}
                  </div>
                </div>

              </div>

            </div>
          )}
        </div>

        {/* Simulation Run History */}
        <div className="glass-panel p-6 rounded-3xl" id="simulation-history-panel">
          <h3 className="text-lg font-bold font-outfit text-white mb-6 flex items-center gap-2">
            <History size={20} className="text-slate-400" />
            Simulation History
          </h3>

          <div className="max-h-72 overflow-y-auto pr-1 space-y-2.5" id="simulation-history-list">
            {history.length > 0 ? (
              history.map((item) => (
                <div 
                  key={item.id}
                  onClick={() => loadHistoryItem(item)}
                  className="p-3 rounded-xl border border-slate-800 bg-slate-800/20 hover:bg-slate-800/40 hover:border-slate-700/80 cursor-pointer flex justify-between items-center transition-colors"
                >
                  <div className="overflow-hidden pr-2">
                    <p className="text-xs font-bold text-slate-200 truncate">{item.campaign_name}</p>
                    <p className="text-[10px] text-slate-500 mt-0.5 truncate">
                      {item.platform} • ${item.spend}
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <span className={`text-[11px] font-bold px-1.5 py-0.5 rounded ${
                      item.success_score >= 70 
                        ? "bg-emerald-500/10 text-brand-emerald" 
                        : item.success_score >= 45 
                          ? "bg-indigo-500/10 text-brand-indigo" 
                          : "bg-rose-500/10 text-brand-rose"
                    }`}>
                      {item.success_score}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 text-center py-8">No past simulations found.</p>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
