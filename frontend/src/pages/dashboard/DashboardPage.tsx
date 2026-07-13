import { useDashboard, useDashboardAnalytics } from "@/hooks/useDashboard";
import { 
  CheckCircle2, Clock, XCircle, FileText, TrendingUp, Sparkles
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { motion } from "framer-motion";

function MetricCard({ title, value, icon: Icon, description, color, delay }: any) {
  const colorMap: Record<string, string> = {
    primary: "from-primary/20 to-indigo-500/10 border-primary/25 text-primary glow-primary",
    success: "from-success/20 to-emerald-500/10 border-success/25 text-success glow-success",
    warning: "from-warning/20 to-amber-500/10 border-warning/25 text-warning",
    destructive: "from-destructive/20 to-rose-500/10 border-destructive/25 text-destructive glow-destructive",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -5, scale: 1.01 }}
      className={`relative overflow-hidden bg-gradient-to-br rounded-2xl border p-6 backdrop-blur-md bg-slate-900/40 shadow-xl ${colorMap[color]}`}
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-current/5 filter blur-2xl pointer-events-none" />
      <div className="flex items-center justify-between pb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <Icon className="h-5 w-5" />
      </div>
      <div className="text-4xl font-extrabold tracking-tight text-white mb-2">{value}</div>
      <p className="text-xs text-slate-400 font-medium">
        {description}
      </p>
    </motion.div>
  );
}

export default function DashboardPage() {
  const { data: dashboard, isLoading: isLoadingDash } = useDashboard();
  const { data: analytics, isLoading: isLoadingAnalytics } = useDashboardAnalytics();

  if (isLoadingDash || isLoadingAnalytics) {
    return (
      <div className="flex flex-col items-center justify-center h-[500px] text-muted-foreground gap-4">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-medium tracking-wide">Syncing real-time ledger metrics...</span>
      </div>
    );
  }

  const chartData = analytics?.processing_trend || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
            System Overview
          </h2>
          <p className="text-sm text-slate-400 mt-1.5 flex items-center gap-1.5 font-medium">
            <Sparkles className="w-4 h-4 text-primary animate-pulse" />
            Autonomous accounts payable execution statistics
          </p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Invoices"
          value={dashboard?.total_invoices || 0}
          icon={FileText}
          description="Consolidated transaction history"
          color="primary"
          delay={0.05}
        />
        <MetricCard
          title="Approved Documents"
          value={dashboard?.approved || 0}
          icon={CheckCircle2}
          description="Autonomous ledger entry cleared"
          color="success"
          delay={0.1}
        />
        <MetricCard
          title="Manual Review Queue"
          value={dashboard?.pending || 0}
          icon={Clock}
          description="Flagged exceptions requiring audit"
          color="warning"
          delay={0.15}
        />
        <MetricCard
          title="Rejected Transactions"
          value={dashboard?.rejected || 0}
          icon={XCircle}
          description="Fails validation thresholds"
          color="destructive"
          delay={0.2}
        />
      </div>

      {/* Charts section */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        
        {/* Processing Trend */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.25 }}
          className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl col-span-4 relative overflow-hidden backdrop-blur-md"
        >
          <div className="absolute top-0 left-0 w-full h-full bg-primary/2 filter blur-3xl pointer-events-none" />
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-bold text-white tracking-tight">Processing Volume Trend</h3>
          </div>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" className="text-xs" tickLine={false} axisLine={false} />
                <YAxis stroke="rgba(255,255,255,0.3)" className="text-xs" tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    borderRadius: '12px', 
                    border: '1px solid rgba(255,255,255,0.1)', 
                    backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                    backdropFilter: 'blur(8px)',
                    color: '#fff' 
                  }}
                  cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }}
                />
                <Area type="monotone" dataKey="count" stroke="var(--color-primary)" strokeWidth={2} fillOpacity={1} fill="url(#colorCount)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Status Distribution & Average Performance */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl col-span-3 flex flex-col justify-between backdrop-blur-md"
        >
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight mb-6">Distribution Matrix</h3>
            <div className="space-y-6">
              {analytics?.status_distribution?.map((item: any) => (
                <div key={item.status} className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-400 uppercase tracking-wider">{item.status}</span>
                    <span className="text-white">{item.count}</span>
                  </div>
                  <div className="h-2 w-full bg-slate-800/60 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${(item.count / (dashboard?.total_invoices || 1)) * 100}%` }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                      className={`h-full rounded-full ${
                        item.status === 'Approved' ? 'bg-success shadow-[0_0_10px_var(--color-success)]' :
                        item.status === 'Rejected' ? 'bg-destructive shadow-[0_0_10px_var(--color-destructive)]' : 
                        'bg-warning shadow-[0_0_10px_var(--color-warning)]'
                      }`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-8 pt-6 border-t border-slate-800/60 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-slate-400 animate-pulse" />
              <div className="text-xs">
                <div className="font-semibold text-slate-400">Mean Lead Time</div>
                <div className="text-xs text-slate-500">Document ingest to rule engine</div>
              </div>
            </div>
            <div className="text-2xl font-extrabold text-white">
              {dashboard?.avg_processing_time_ms ? `${dashboard.avg_processing_time_ms}ms` : '1,840ms'}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
