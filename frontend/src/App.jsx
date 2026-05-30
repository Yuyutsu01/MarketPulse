import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CampaignUpload from "./pages/CampaignUpload";
import Analytics from "./pages/Analytics";
import Predictions from "./pages/Predictions";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const savedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
      }
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-brand-indigo/30 border-t-brand-indigo rounded-full animate-spin" />
      </div>
    );
  }

  // Authentication Guard for Private Routes
  const ProtectedLayout = ({ children }) => {
    if (!user) {
      return <Navigate to="/login" replace />;
    }

    return (
      <div className="min-h-screen bg-dark-900 flex flex-col lg:flex-row relative">
        {/* Decorative background visual elements */}
        <div className="bg-blob-indigo top-[10%] left-[-10%] opacity-70 animate-pulse-slow" />
        <div className="bg-blob-purple bottom-[15%] right-[-10%] opacity-60 animate-pulse-slow" />
        
        {/* Navigation Sidebar */}
        <Sidebar user={user} onLogout={handleLogout} />
        
        {/* Main Content Area */}
        <main className="flex-1 min-w-0 p-6 lg:p-8 lg:pl-[20rem] xl:pl-[21rem] pt-20 lg:pt-8 relative z-10 overflow-y-auto max-h-screen">
          <div className="max-w-6xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    );
  };

  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route 
          path="/login" 
          element={user ? <Navigate to="/" replace /> : <Login onLoginSuccess={handleLoginSuccess} />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/" replace /> : <Register onLoginSuccess={handleLoginSuccess} />} 
        />

        {/* Protected Routes */}
        <Route 
          path="/" 
          element={
            <ProtectedLayout>
              <Dashboard />
            </ProtectedLayout>
          } 
        />
        <Route 
          path="/upload" 
          element={
            <ProtectedLayout>
              <CampaignUpload />
            </ProtectedLayout>
          } 
        />
        <Route 
          path="/analytics" 
          element={
            <ProtectedLayout>
              <Analytics />
            </ProtectedLayout>
          } 
        />
        <Route 
          path="/predict" 
          element={
            <ProtectedLayout>
              <Predictions />
            </ProtectedLayout>
          } 
        />

        {/* Catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
