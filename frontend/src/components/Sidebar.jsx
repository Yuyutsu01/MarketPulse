import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { 
  LayoutDashboard, 
  UploadCloud, 
  Users, 
  BrainCircuit, 
  LogOut, 
  Menu, 
  X,
  LineChart
} from "lucide-react";

export default function Sidebar({ user, onLogout }) {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Campaign Upload", path: "/upload", icon: UploadCloud },
    { name: "Audience Analytics", path: "/analytics", icon: Users },
    { name: "Predict Success", path: "/predict", icon: BrainCircuit },
  ];

  const handleLogoutClick = () => {
    onLogout();
    navigate("/login");
  };

  const navClasses = (path) => {
    const isActive = location.pathname === path;
    return `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
      isActive 
        ? "bg-gradient-to-r from-brand-indigo to-brand-violet text-white shadow-lg shadow-indigo-500/20" 
        : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/40"
    }`;
  };

  return (
    <>
      {/* Mobile Toggle Button */}
      <button 
        id="btn-mobile-nav-toggle"
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2.5 rounded-xl glass-panel text-slate-200 hover:bg-slate-800"
        aria-label="Toggle navigation menu"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar Panel */}
      <aside 
        id="sidebar-navigation"
        className={`fixed inset-y-0 left-0 z-40 w-64 lg:w-72 glass-panel border-r border-slate-800/50 flex flex-col justify-between transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-6 flex flex-col h-full">
          {/* Logo Brand */}
          <div className="flex items-center gap-3 mb-8 mt-4 lg:mt-0">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-brand-indigo to-brand-violet shadow-lg shadow-indigo-500/35">
              <LineChart size={24} className="text-white" />
            </div>
            <div>
              <span className="font-outfit font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
                MarketPulse
              </span>
              <span className="ml-1 text-[10px] font-semibold text-brand-cyan tracking-widest uppercase">
                AI
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 space-y-1.5" id="nav-links-container">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link 
                  key={item.path} 
                  to={item.path} 
                  onClick={() => setIsOpen(false)}
                  className={navClasses(item.path)}
                  id={`nav-link-${item.name.toLowerCase().replace(" ", "-")}`}
                >
                  <Icon size={20} />
                  <span className="font-medium text-sm">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Section & Logout */}
          <div className="mt-auto border-t border-slate-800/60 pt-6">
            {user && (
              <div className="flex items-center gap-3 mb-4 px-2" id="user-profile-badge">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-cyan to-brand-indigo flex items-center justify-center font-bold text-white shadow-md shadow-cyan-500/10">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="overflow-hidden">
                  <p className="text-sm font-semibold text-slate-200 truncate">{user.name}</p>
                  <p className="text-xs text-slate-500 truncate">{user.email}</p>
                </div>
              </div>
            )}
            
            <button 
              id="btn-logout"
              onClick={handleLogoutClick}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-brand-rose hover:bg-rose-500/10 transition-all duration-200 font-medium text-sm"
            >
              <LogOut size={20} />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Backdrop for mobile */}
      {isOpen && (
        <div 
          onClick={() => setIsOpen(false)}
          className="lg:hidden fixed inset-0 z-30 bg-black/60 backdrop-blur-sm"
        />
      )}
    </>
  );
}
