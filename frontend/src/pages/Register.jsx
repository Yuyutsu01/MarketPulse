import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, User, ArrowRight, LineChart } from "lucide-react";
import api from "../services/api";

export default function Register({ onLoginSuccess }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setError("Please fill in all fields");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError("");
    setStatusMsg("Creating account...");

    try {
      // 1. Register User
      await api.post("/api/auth/register", {
        name,
        email,
        password,
      });

      setStatusMsg("Generating marketing intelligence database (seeding ~1000 records)...");

      // 2. Perform Auto-Login
      const formData = new FormData();
      formData.append("username", email);
      formData.append("password", password);

      const loginResponse = await api.post("/api/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const { access_token } = loginResponse.data;
      localStorage.setItem("token", access_token);

      // 3. Get User Details
      const userResponse = await api.get("/api/auth/me");
      const user = userResponse.data;
      localStorage.setItem("user", JSON.stringify(user));

      setStatusMsg("Finalizing...");
      
      onLoginSuccess(user);
      navigate("/");
      
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Registration failed. This email may already be in use."
      );
      setStatusMsg("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 overflow-hidden bg-dark-900">
      {/* Decorative Blur Blobs */}
      <div className="bg-blob-indigo top-[-10%] right-[-10%] animate-pulse-slow" />
      <div className="bg-blob-purple bottom-[-10%] left-[-10%] animate-pulse-slow" />

      <div className="w-full max-w-md relative z-10">
        {/* Branding header */}
        <div className="flex flex-col items-center mb-8">
          <div className="p-3.5 rounded-2xl bg-gradient-to-br from-brand-indigo to-brand-violet shadow-xl shadow-indigo-500/30 mb-4 animate-float">
            <LineChart size={32} className="text-white" />
          </div>
          <h1 className="font-outfit font-extrabold text-3xl tracking-tight text-white flex items-center gap-1.5">
            MarketPulse <span className="text-xs font-semibold text-brand-cyan uppercase tracking-widest bg-cyan-950/40 border border-brand-cyan/20 px-2 py-0.5 rounded-md">AI</span>
          </h1>
          <p className="text-slate-400 text-sm mt-2 text-center">
            Sign up to unlock data-driven marketing predictions
          </p>
        </div>

        {/* Register Form Panel */}
        <div className="glass-panel p-8 rounded-3xl" id="register-card-panel">
          <h2 className="text-2xl font-bold font-outfit text-white mb-6">Create Account</h2>

          {error && (
            <div 
              id="register-error-alert"
              className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-brand-rose text-sm font-medium"
            >
              {error}
            </div>
          )}

          {statusMsg && !error && (
            <div 
              id="register-status-msg"
              className="mb-6 p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-brand-cyan text-sm font-medium flex items-center gap-3"
            >
              <div className="w-4 h-4 border-2 border-cyan-500/30 border-t-brand-cyan rounded-full animate-spin" />
              <span>{statusMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" id="register-form">
            <div>
              <label htmlFor="name-input" className="block text-slate-300 text-xs font-semibold uppercase tracking-wider mb-2">
                Full Name
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <User size={18} />
                </span>
                <input
                  id="name-input"
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="glass-input w-full pl-11 pr-4 py-3 rounded-xl text-sm"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="email-input" className="block text-slate-300 text-xs font-semibold uppercase tracking-wider mb-2">
                Work Email
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <Mail size={18} />
                </span>
                <input
                  id="email-input"
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="glass-input w-full pl-11 pr-4 py-3 rounded-xl text-sm"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="password-input" className="block text-slate-300 text-xs font-semibold uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <Lock size={18} />
                </span>
                <input
                  id="password-input"
                  type="password"
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="glass-input w-full pl-11 pr-4 py-3 rounded-xl text-sm"
                  required
                />
              </div>
            </div>

            <button
              id="btn-register-submit"
              type="submit"
              disabled={loading}
              className="w-full glass-btn-primary py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 mt-8 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-800/60 text-center">
            <span className="text-slate-400 text-sm">
              Already have an account?{" "}
              <Link 
                to="/login" 
                id="link-go-to-login"
                className="text-brand-indigo hover:text-brand-violet font-semibold transition-colors"
              >
                Sign in here
              </Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
