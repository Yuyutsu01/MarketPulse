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
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold font-outfit text-white tracking-tight">
            Dashboard Analytics
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time campaign overview and execution trends.
          </p>
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

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" id="kpi-grid">
        <KpiCard
          id="kpi-card-roi"
          title="Return on Investment"
          value={`${kpis?.roi}%`}
          icon={TrendingUp}
          subtext={`Rev: $${kpis?.total_revenue.toLocaleString()}`}
          change={12.4}
          isPositive={kpis?.roi >= 0}
          tooltip="Total Revenue minus Spend, divided by Spend. Higher values represent better return efficiency."
        />
        <KpiCard
          id="kpi-card-ctr"
          title="Click-Through Rate"
          value={`${kpis?.ctr}%`}
          icon={MousePointerClick}
          subtext={`Clicks: ${kpis?.total_clicks.toLocaleString()}`}
          change={4.2}
          isPositive={true}
          tooltip="The percentage of campaign impressions that resulted in clicks."
        />
        <KpiCard
          id="kpi-card-cpc"
          title="Cost Per Click"
          value={`$${kpis?.cpc}`}
          icon={DollarSign}
          subtext={`Spend: $${kpis?.total_spend.toLocaleString()}`}
          change={-3.1}
          isPositive={true}
          tooltip="Average cost paid for each individual ad click. Lower values indicate cheaper traffic."
        />
        <KpiCard
          id="kpi-card-cvr"
          title="Conversion Rate"
          value={`${kpis?.conversion_rate}%`}
          icon={Activity}
          subtext={`Convs: ${kpis?.total_conversions.toLocaleString()}`}
          change={2.8}
          isPositive={true}
          tooltip="The percentage of ad clicks that successfully completed a conversion action."
        />
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Timeseries Area Chart (Performance Over Time) */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl flex flex-col justify-between" id="chart-timeseries-panel">
          <div className="mb-6">
            <h3 className="text-lg font-bold font-outfit text-white">Campaign Performance Trends</h3>
            <p className="text-xs text-slate-400 mt-0.5">Spend and revenue trajectory over the past 30 days</p>
          </div>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts?.timeseries} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip />
                <Legend verticalAlign="top" height={36} />
                <Area type="monotone" name="Spend ($)" dataKey="spend" stroke="#8b5cf6" strokeWidth={2} fillOpacity={1} fill="url(#colorSpend)" />
                <Area type="monotone" name="Revenue ($)" dataKey="revenue" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorRevenue)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Spend Share Donut Chart */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col justify-between" id="chart-spend-share-panel">
          <div className="mb-4">
            <h3 className="text-lg font-bold font-outfit text-white">Spend Share by Platform</h3>
            <p className="text-xs text-slate-400 mt-0.5">Budget distribution across marketing channels</p>
          </div>
          <div className="h-64 w-full relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts?.platform_shares}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="spend"
                  nameKey="platform"
                >
                  {charts?.platform_shares.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Center Label */}
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-widest">Total Spend</span>
              <span className="text-2xl font-extrabold font-outfit text-white mt-1">
                ${kpis?.total_spend >= 1000 ? `${(kpis?.total_spend / 1000).toFixed(1)}k` : kpis?.total_spend}
              </span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-4">
            {charts?.platform_shares.map((entry, index) => (
              <div key={entry.platform} className="flex items-center gap-2">
                <span 
                  className="w-2.5 h-2.5 rounded-full inline-block shrink-0" 
                  style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} 
                />
                <span className="text-xs text-slate-300 truncate">{entry.platform}</span>
                <span className="text-[10px] text-slate-500 font-semibold">
                  ({((entry.spend / kpis?.total_spend) * 100).toFixed(0)}%)
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Grouped Comparison Chart */}
      <div className="glass-panel p-6 rounded-3xl" id="chart-comparison-panel">
        <div className="mb-6">
          <h3 className="text-lg font-bold font-outfit text-white">Platform Efficiency Comparison</h3>
          <p className="text-xs text-slate-400 mt-0.5">Side-by-side ROI and Conversion Rate mapping per channel</p>
        </div>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={charts?.platform_comparisons} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="platform" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
              <Tooltip />
              <Legend verticalAlign="top" height={36} />
              <Bar name="ROI (%)" dataKey="roi" fill="#6366f1" radius={[4, 4, 0, 0]}>
                {charts?.platform_comparisons.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.roi >= 0 ? "#6366f1" : "#f43f5e"} />
                ))}
              </Bar>
              <Bar name="Conversion Rate (%)" dataKey="conversion_rate" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
