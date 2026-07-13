import { Outlet, NavLink, useLocation } from "react-router-dom";
import { LayoutDashboard, Upload, History, Zap, Sparkles, Settings, Building2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Overview" },
  { to: "/upload", icon: Upload, label: "Upload Center" },
  { to: "/history", icon: History, label: "Invoice History" },
  { to: "/vendors", icon: Building2, label: "Vendors & POs" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar */}
      <aside className="hidden md:flex w-72 flex-col border-r border-slate-800/80 bg-slate-950/40 backdrop-blur-md relative z-10">
        {/* Glow behind logo */}
        <div className="absolute top-0 left-0 w-full h-32 bg-primary/5 filter blur-3xl pointer-events-none" />
        
        {/* Brand/Logo */}
        <div className="flex items-center gap-3.5 px-7 py-6 border-b border-slate-800/50">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-indigo-400 text-white shadow-lg shadow-primary/20">
            <Zap className="w-5.5 h-5.5 animate-pulse" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
              FinanceFlow AI
            </h1>
            <p className="text-[11px] text-primary/80 font-medium tracking-wider uppercase">AP Copilot</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2.5">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-medium transition-all duration-300 relative group overflow-hidden ${
                  isActive
                    ? "text-primary bg-primary/5 border border-primary/20 shadow-[inset_0_1px_12px_rgba(168,85,247,0.05)]"
                    : "text-slate-400 hover:text-slate-100 hover:bg-slate-900/40 border border-transparent"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${isActive ? "text-primary" : "text-slate-400"}`} />
                  <span className="relative z-10">{label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="active-indicator"
                      className="absolute right-0 top-1/4 w-1 h-1/2 bg-primary rounded-l-full shadow-[0_0_12px_var(--color-primary)]"
                    />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Info card in sidebar */}
        <div className="p-4 mx-4 mb-6 border border-slate-800/80 rounded-xl bg-slate-900/20 backdrop-blur-sm relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 filter blur-xl pointer-events-none" />
          <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-primary">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AP Validation Engine</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-normal">
            Autonomous invoice processing with deterministic business rules & generative explanations.
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Decorative subtle ambient lights */}
        <div className="absolute top-0 left-1/4 w-[500px] h-[300px] bg-primary/5 filter blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[300px] bg-indigo-500/5 filter blur-3xl pointer-events-none" />
        
        <main className="flex-1 overflow-y-auto relative z-10">
          <div className="max-w-7xl mx-auto px-8 py-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  );
}
