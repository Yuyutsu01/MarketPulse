import React from "react";
import { Info } from "lucide-react";

export default function KpiCard({ title, value, icon: Icon, subtext, change, isPositive, tooltip, id }) {
  return (
    <div 
      id={id}
      className="glass-panel glass-panel-hover p-6 rounded-2xl relative overflow-hidden flex flex-col justify-between"
    >
      {/* Decorative background glow */}
      <div className="absolute -top-10 -right-10 w-24 h-24 bg-white/5 rounded-full blur-xl pointer-events-none" />

      <div className="flex justify-between items-start mb-4">
        <span className="text-slate-400 text-xs font-semibold tracking-wider uppercase font-outfit">
          {title}
        </span>
        {Icon && (
          <div className="p-2 rounded-xl bg-slate-800/60 text-slate-300">
            <Icon size={18} />
          </div>
        )}
      </div>

      <div className="flex flex-col">
        <h3 className="text-3xl font-extrabold font-outfit text-white tracking-tight leading-none mb-2">
          {value}
        </h3>
        
        <div className="flex items-center gap-2 mt-1">
          {change !== undefined && (
            <span className={`text-xs font-bold px-1.5 py-0.5 rounded-md ${
              isPositive 
                ? "bg-emerald-500/10 text-brand-emerald" 
                : "bg-rose-500/10 text-brand-rose"
            }`}>
              {isPositive ? "+" : ""}{change}%
            </span>
          )}
          <span className="text-xs text-slate-500 truncate">
            {subtext}
          </span>
        </div>
      </div>

      {tooltip && (
        <div className="absolute bottom-3 right-3 group cursor-help">
          <Info size={12} className="text-slate-600 hover:text-slate-400 transition-colors" />
          <div className="absolute right-0 bottom-5 w-48 p-2 rounded-lg bg-dark-900 border border-slate-700 text-[10px] text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl z-20">
            {tooltip}
          </div>
        </div>
      )}
    </div>
  );
}
