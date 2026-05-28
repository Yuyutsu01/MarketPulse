import React, { useEffect, useState } from "react";
import { Users, Laptop, Globe, Clock, Sparkles } from "lucide-react";
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell 
} from "recharts";
import api from "../services/api";

export default function Analytics() {
  const [audienceData, setAudienceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAudienceData = async () => {
      try {
        const response = await api.get("/api/analytics/audience");
        setAudienceData(response.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load audience insights. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchAudienceData();
  }, []);

  const PIE_COLORS = ["#6366f1", "#06b6d4", "#8b5cf6"];

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse p-1" id="analytics-loading-view">
        <div className="h-8 w-48 bg-slate-800 rounded-lg" />
        <div className="h-24 bg-slate-800/40 rounded-3xl animate-shimmer" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-80 bg-slate-800/40 rounded-3xl animate-shimmer" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" id="analytics-view">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold font-outfit text-white tracking-tight">
          Audience Insights
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Detailed performance breakdown by device, demographics, time, and locations.
        </p>
      </div>

      {error && (
        <div 
          id="analytics-error-alert"
          className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-brand-rose text-sm font-medium"
        >
          {error}
        </div>
      )}

      {/* Account Highlights Insight Card */}
      <div className="glass-panel p-6 rounded-3xl border border-brand-indigo/20 bg-indigo-950/10 flex flex-col md:flex-row items-start md:items-center gap-4 justify-between" id="analytics-highlight-card">
        <div className="flex gap-4">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-brand-indigo to-brand-violet text-white shadow-lg shadow-indigo-500/25 shrink-0">
            <Sparkles size={22} className="animate-pulse" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white font-outfit">Core Segment Intelligence</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Based on historical aggregates, **Mobile** device formats and audience segments aged **25-34** demonstrate the highest overall conversion densities, peaking around **7 PM - 10 PM** on Instagram.
            </p>
          </div>
        </div>
        <div className="px-3 py-1.5 rounded-lg bg-indigo-900/30 border border-brand-indigo/30 text-[10px] uppercase font-bold text-brand-indigo tracking-wider self-start md:self-auto">
          AI Analytics Active
        </div>
      </div>

      {/* Grid of Demographics Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* 1. Device Usage Breakdown */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col justify-between" id="chart-device-panel">
          <div className="mb-4">
            <h3 className="text-lg font-bold font-outfit text-white flex items-center gap-2">
              <Laptop size={18} className="text-brand-indigo" />
              Device Performance Share
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Conversion share and conversion rate by device type</p>
          </div>
          <div className="h-60 w-full flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={audienceData?.devices}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="conversions"
                  nameKey="device"
                >
                  {audienceData?.devices.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value} convs`} />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="absolute text-center flex flex-col items-center">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Top device</span>
              <span className="text-xl font-extrabold text-white mt-0.5">
                {audienceData?.devices[0]?.device || "Mobile"}
              </span>
            </div>
          </div>
          <div className="flex justify-around items-center border-t border-slate-800/60 pt-4 mt-2">
            {audienceData?.devices.map((d, index) => (
              <div key={d.device} className="text-center">
                <div className="flex items-center justify-center gap-1.5">
                  <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} />
                  <span className="text-xs font-semibold text-slate-300">{d.device}</span>
                </div>
                <p className="text-sm font-extrabold text-white mt-1">{d.conversion_rate}% CVR</p>
                <p className="text-[10px] text-slate-500 font-medium">Avg CPC: ${d.cpc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 2. Demographic Age Cohorts */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col justify-between" id="chart-demographics-panel">
          <div className="mb-4">
            <h3 className="text-lg font-bold font-outfit text-white flex items-center gap-2">
              <Users size={18} className="text-brand-cyan" />
              Demographic Conversion Density
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Conversions and conversion efficiency across age groups</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={audienceData?.age_groups} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="age_group" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip />
                <Legend verticalAlign="top" height={36} />
                <Bar name="Conversions" dataKey="conversions" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar name="Conversion Rate (%)" dataKey="conversion_rate" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Geographic Performance */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col justify-between" id="chart-geography-panel">
          <div className="mb-4">
            <h3 className="text-lg font-bold font-outfit text-white flex items-center gap-2">
              <Globe size={18} className="text-brand-emerald" />
              Geographic Acquisition Efficiency
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Customer Acquisition Cost (CAC) vs. conversion volume per country</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={audienceData?.geography} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="geography" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip />
                <Legend verticalAlign="top" height={36} />
                <Bar name="CAC ($)" dataKey="cac" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar name="Conversions" dataKey="conversions" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Time-of-Day Performance (Hourly Engagement) */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col justify-between" id="chart-hourly-panel">
          <div className="mb-4">
            <h3 className="text-lg font-bold font-outfit text-white flex items-center gap-2">
              <Clock size={18} className="text-brand-violet" />
              Hourly Conversion Profiles
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Conversion rate fluctuations across hours of the day (0-23)</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={audienceData?.hourly_performance} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip />
                <Line type="monotone" name="Conversion Rate (%)" dataKey="conversion_rate" stroke="#8b5cf6" strokeWidth={2.5} dot={false} />
                <Line type="monotone" name="Conversions" dataKey="conversions" stroke="#6366f1" strokeWidth={1.5} dot={false} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
