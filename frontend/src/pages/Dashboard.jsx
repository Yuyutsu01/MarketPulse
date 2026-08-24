import React, { useEffect, useState } from "react";
import { 
  TrendingUp, 
  MousePointerClick, 
  DollarSign, 
  Activity, 
  RefreshCw, 
  Eye, 
  ShoppingBag,
  Percent
} from "lucide-react";
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar 
} from "recharts";
import api from "../services/api";
import KpiCard from "../components/KpiCard";
import logoImg from "../assets/MarketPulse.png";

export default function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [charts, setCharts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setError("");
      const [kpiRes, chartsRes] = await Promise.all([
        api.get("/api/analytics/kpis"),
        api.get("/api/analytics/charts")
      ]);
      setKpis(kpiRes.data);
      setCharts(chartsRes.data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch dashboard intelligence. Please try again.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const PIE_COLORS = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f43f5e"];

  const customTooltipProps = {
    contentStyle: { backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "12px", color: "#ffffff" },
    itemStyle: { color: "#ffffff" },
    labelStyle: { color: "#ffffff" }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse p-1" id="dashboard-loading-view">
        <div className="flex justify-between items-center">
          <div className="h-8 w-48 bg-slate-800 rounded-lg" />
          <div className="h-10 w-24 bg-slate-800 rounded-lg" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-800/50 rounded-2xl border border-slate-800/40 animate-shimmer" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 bg-slate-800/40 rounded-3xl border border-slate-800/40 animate-shimmer" />
          <div className="h-96 bg-slate-800/40 rounded-3xl border border-slate-800/40 animate-shimmer" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" id="dashboard-view">
      {/* Header with Logo */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <div className="p-2 rounded-2xl glass-panel border border-slate-800 shadow-xl hidden sm:block">
            <img src={logoImg} alt="MarketPulse AI Logo" className="w-12 h-12 object-contain rounded-xl" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-extrabold font-outfit text-white tracking-tight">
                Dashboard Analytics
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-brand-indigo/20 text-brand-indigo border border-brand-indigo/30 uppercase tracking-widest">
                Enterprise AI
              </span>
            </div>
            <p className="text-slate-400 text-sm mt-1">
              Real-time campaign overview, attribution performance, and execution trends.
            </p>
          </div>
        </div>

        <button
          id="btn-refresh-dashboard"
          onClick={handleRefresh}
          disabled={refreshing}
          className="glass-btn-secondary px-4 py-2.5 rounded-xl text-sm flex items-center gap-2"
        >
          <RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div 
          id="dashboard-error-alert"
          className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-brand-rose text-sm font-medium"
        >
          {error}
        </div>
      )}

      {/* Primary KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" id="kpi-cards-grid">
        <KpiCard 
          id="kpi-card-roi"
          title="Return on Investment" 
          value={`${kpis?.roi}%`} 
          subtitle="Overall ROI yield" 
          icon={TrendingUp}
          variant="emerald"
        />
        <KpiCard 
          id="kpi-card-ctr"
          title="Click-Through Rate" 
          value={`${kpis?.ctr}%`} 
          subtitle="Engagement efficiency" 
          icon={MousePointerClick}
          variant="indigo"
        />
        <KpiCard 
          id="kpi-card-cpc"
          title="Cost Per Click" 
          value={`$${kpis?.cpc}`} 
          subtitle="Average CPC spend" 
          icon={DollarSign}
          variant="cyan"
        />
        <KpiCard 
          id="kpi-card-conversions"
          title="Total Conversions" 
          value={kpis?.total_conversions?.toLocaleString()} 
          subtitle="Acquisition volume" 
          icon={ShoppingBag}
          variant="amber"
        />
      </div>

      {/* Secondary Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" id="secondary-kpi-grid">
        <div className="glass-panel p-4 rounded-2xl border border-slate-800/60">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Total Spend</span>
          <p className="text-lg font-bold font-outfit text-white mt-1">${kpis?.total_spend?.toLocaleString()}</p>
        </div>
        <div className="glass-panel p-4 rounded-2xl border border-slate-800/60">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Total Impressions</span>
          <p className="text-lg font-bold font-outfit text-white mt-1">{kpis?.total_impressions?.toLocaleString()}</p>
        </div>
        <div className="glass-panel p-4 rounded-2xl border border-slate-800/60">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Conversion Rate</span>
          <p className="text-lg font-bold font-outfit text-white mt-1">{kpis?.conversion_rate}%</p>
        </div>
        <div className="glass-panel p-4 rounded-2xl border border-slate-800/60">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">CAC</span>
          <p className="text-lg font-bold font-outfit text-white mt-1">${kpis?.cac}</p>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Timeseries Area Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl" id="timeseries-chart-panel">
          <h3 className="text-lg font-bold font-outfit text-white mb-4 flex items-center gap-2">
            <Activity size={20} className="text-brand-indigo" />
            Performance Trends Over Time
          </h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts?.timeseries || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="spendGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="conversionsGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip {...customTooltipProps} />
                <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
                <Area type="monotone" dataKey="spend" name="Daily Spend ($)" stroke="#6366f1" strokeWidth={2.5} fillOpacity={1} fill="url(#spendGradient)" />
                <Area type="monotone" dataKey="conversions" name="Conversions" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#conversionsGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Platform Share Donut Chart */}
        <div className="glass-panel p-6 rounded-3xl" id="platform-share-chart-panel">
          <h3 className="text-lg font-bold font-outfit text-white mb-4 flex items-center gap-2">
            <Eye size={20} className="text-brand-cyan" />
            Platform Spend Share
          </h3>
          <div className="h-80 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts?.platform_shares || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={95}
                  paddingAngle={5}
                  dataKey="spend"
                  nameKey="platform"
                >
                  {(charts?.platform_shares || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} stroke="#0f172a" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip {...customTooltipProps} formatter={(val) => `$${val.toLocaleString()}`} />
                <Legend wrapperStyle={{ fontSize: "11px" }} layout="horizontal" align="center" verticalAlign="bottom" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Cross-Platform Comparison Bar Chart */}
      <div className="glass-panel p-6 rounded-3xl" id="platform-comparison-chart-panel">
        <h3 className="text-lg font-bold font-outfit text-white mb-4 flex items-center gap-2">
          <Percent size={20} className="text-brand-amber" />
          Cross-Platform ROI Efficiency Comparison (%)
        </h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={charts?.platform_comparisons || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
              <XAxis dataKey="platform" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
              <Tooltip {...customTooltipProps} />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
              <Bar dataKey="roi" name="ROI (%)" fill="#6366f1" radius={[8, 8, 0, 0]} />
              <Bar dataKey="conversion_rate" name="Conversion Rate (%)" fill="#06b6d4" radius={[8, 8, 0, 0]} />
              <Bar dataKey="ctr" name="CTR (%)" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
