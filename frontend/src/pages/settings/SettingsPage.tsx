import { useState, useEffect } from "react";
import { useSettings, useUpdateSettings } from "@/hooks/useSettings";
import { Shield, Percent, Clock, Sparkles, Save, RotateCcw, Mail, Link as LinkIcon, Database } from "lucide-react";
import { motion } from "framer-motion";

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings();
  const { mutate: updateSettings, isPending } = useUpdateSettings();

  const [tolerance, setTolerance] = useState(5.0);
  const [maxAge, setMaxAge] = useState(365);
  const [requireGst, setRequireGst] = useState(true);
  const [requirePo, setRequirePo] = useState(true);
  
  // New Validation Settings
  const [duplicateDays, setDuplicateDays] = useState(90);
  const [minConfidence, setMinConfidence] = useState(85);
  const [requireLineItems, setRequireLineItems] = useState(true);
  
  // New Integration Settings
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [emailServer, setEmailServer] = useState("imap.gmail.com");
  const [emailAddress, setEmailAddress] = useState("");
  const [emailPassword, setEmailPassword] = useState("");
  
  const [erpEnabled, setErpEnabled] = useState(false);
  const [erpWebhook, setErpWebhook] = useState("");

  // Sync state with loaded settings
  useEffect(() => {
    if (settings) {
      setTolerance(settings.PO_TOLERANCE_PERCENT ?? 5.0);
      setMaxAge(settings.MAX_INVOICE_AGE_DAYS ?? 365);
      setRequireGst(settings.REQUIRE_GST ?? true);
      setRequirePo(settings.REQUIRE_PO ?? true);
      
      setDuplicateDays(settings.DUPLICATE_DETECTION_DAYS ?? 90);
      setMinConfidence(settings.MIN_CONFIDENCE_THRESHOLD ?? 85);
      setRequireLineItems(settings.REQUIRE_LINE_ITEMS_MATCH ?? true);
      
      setEmailEnabled(settings.EMAIL_INGESTION_ENABLED ?? false);
      setEmailServer(settings.EMAIL_SERVER ?? "imap.gmail.com");
      setEmailAddress(settings.EMAIL_ADDRESS ?? "");
      setEmailPassword(settings.EMAIL_PASSWORD ?? "");
      
      setErpEnabled(settings.ERP_SYNC_ENABLED ?? false);
      setErpWebhook(settings.ERP_WEBHOOK_URL ?? "");
    }
  }, [settings]);

  const handleSave = () => {
    updateSettings({
      PO_TOLERANCE_PERCENT: tolerance,
      MAX_INVOICE_AGE_DAYS: maxAge,
      REQUIRE_GST: requireGst,
      REQUIRE_PO: requirePo,
      DUPLICATE_DETECTION_DAYS: duplicateDays,
      MIN_CONFIDENCE_THRESHOLD: minConfidence,
      REQUIRE_LINE_ITEMS_MATCH: requireLineItems,
      EMAIL_INGESTION_ENABLED: emailEnabled,
      EMAIL_SERVER: emailServer,
      EMAIL_ADDRESS: emailAddress,
      EMAIL_PASSWORD: emailPassword,
      ERP_SYNC_ENABLED: erpEnabled,
      ERP_WEBHOOK_URL: erpWebhook
    });
  };

  const handleReset = () => {
    setTolerance(5.0);
    setMaxAge(365);
    setRequireGst(true);
    setRequirePo(true);
    setDuplicateDays(90);
    setMinConfidence(85);
    setRequireLineItems(true);
    setEmailEnabled(false);
    setEmailServer("imap.gmail.com");
    setEmailAddress("");
    setEmailPassword("");
    setErpEnabled(false);
    setErpWebhook("");
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[500px] text-muted-foreground gap-4">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-medium tracking-wide">Syncing system parameters...</span>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
          System Settings & Integrations
        </h2>
        <p className="text-sm text-slate-400 mt-1.5 flex items-center gap-1.5 font-medium">
          <Sparkles className="w-4 h-4 text-primary animate-pulse" />
          Configure dynamic business thresholds and external system integrations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left Side: Parameters Form */}
        <div className="md:col-span-8 space-y-6">
          
          {/* Strict Policy Rules */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/2 filter blur-3xl pointer-events-none" />
            <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 mb-5 flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary" /> Required Documents Policies
            </h3>
            
            <div className="space-y-6">
              {/* Strict PO Toggle */}
              <div className="flex items-center justify-between p-4.5 rounded-xl border border-slate-850 bg-slate-950/20">
                <div className="space-y-1 pr-4">
                  <div className="text-sm font-bold text-white">Strict Purchase Order Check</div>
                  <div className="text-[11px] text-slate-400 leading-normal font-medium">
                    Flag any incoming invoices that do not reference an active PO in the system database.
                  </div>
                </div>
                <button
                  onClick={() => setRequirePo(!requirePo)}
                  className={`w-12 h-6.5 rounded-full p-1 transition-all duration-300 ${
                    requirePo ? "bg-primary shadow-[0_0_12px_var(--color-primary)]" : "bg-slate-800"
                  }`}
                >
                  <div 
                    className={`bg-white w-4.5 h-4.5 rounded-full shadow-md transform transition-transform duration-300 ${
                      requirePo ? "translate-x-5.5" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>

              {/* Strict GST Toggle */}
              <div className="flex items-center justify-between p-4.5 rounded-xl border border-slate-850 bg-slate-950/20">
                <div className="space-y-1 pr-4">
                  <div className="text-sm font-bold text-white">Require Vendor GST Identification</div>
                  <div className="text-[11px] text-slate-400 leading-normal font-medium">
                    Fail validation if a tax rate &gt; 0% is present but no valid GST number is extracted.
                  </div>
                </div>
                <button
                  onClick={() => setRequireGst(!requireGst)}
                  className={`w-12 h-6.5 rounded-full p-1 transition-all duration-300 ${
                    requireGst ? "bg-primary shadow-[0_0_12px_var(--color-primary)]" : "bg-slate-800"
                  }`}
                >
                  <div 
                    className={`bg-white w-4.5 h-4.5 rounded-full shadow-md transform transition-transform duration-300 ${
                      requireGst ? "translate-x-5.5" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>

              {/* Strict Line Items Toggle */}
              <div className="flex items-center justify-between p-4.5 rounded-xl border border-slate-850 bg-slate-950/20">
                <div className="space-y-1 pr-4">
                  <div className="text-sm font-bold text-white">Strict Line Items Integrity</div>
                  <div className="text-[11px] text-slate-400 leading-normal font-medium">
                    Require that the mathematical sum of all extracted line items exactly equals the extracted subtotal.
                  </div>
                </div>
                <button
                  onClick={() => setRequireLineItems(!requireLineItems)}
                  className={`w-12 h-6.5 rounded-full p-1 transition-all duration-300 ${
                    requireLineItems ? "bg-primary shadow-[0_0_12px_var(--color-primary)]" : "bg-slate-800"
                  }`}
                >
                  <div 
                    className={`bg-white w-4.5 h-4.5 rounded-full shadow-md transform transition-transform duration-300 ${
                      requireLineItems ? "translate-x-5.5" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>
            </div>
          </motion.div>

          {/* Tolerance Thresholds */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md relative"
          >
            <div className="absolute top-0 left-0 w-full h-full bg-primary/1 filter blur-3xl pointer-events-none" />
            <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 mb-6 flex items-center gap-2">
              <Percent className="w-4 h-4 text-primary" /> Variance Tolerance Limits
            </h3>
            
            <div className="space-y-8">
              {/* Tolerance Slider */}
              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider">
                  <span className="text-slate-400">PO Over-Billing Tolerance</span>
                  <span className="text-primary font-black text-sm">{tolerance}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="20"
                  step="0.5"
                  value={tolerance}
                  onChange={(e) => setTolerance(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary focus:outline-none"
                />
                <div className="text-[11px] text-slate-500 leading-normal font-medium mt-1">
                  Allowed percentage variance for an invoice value exceeding its matching Purchase Order. Flagged as manual review if exceeded.
                </div>
              </div>

              {/* Max Age Slider */}
              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider">
                  <span className="text-slate-400">Invoice Age Cut-off</span>
                  <span className="text-primary font-black text-sm">{maxAge} Days</span>
                </div>
                <input
                  type="range"
                  min="30"
                  max="730"
                  step="30"
                  value={maxAge}
                  onChange={(e) => setMaxAge(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary focus:outline-none"
                />
                <div className="text-[11px] text-slate-500 leading-normal font-medium mt-1">
                  Invoices older than this threshold relative to current date will fail policy verification.
                </div>
              </div>

              {/* Duplicate Detection Window Slider */}
              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider">
                  <span className="text-slate-400">Duplicate Detection Window</span>
                  <span className="text-primary font-black text-sm">{duplicateDays} Days</span>
                </div>
                <input
                  type="range"
                  min="30"
                  max="365"
                  step="15"
                  value={duplicateDays}
                  onChange={(e) => setDuplicateDays(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary focus:outline-none"
                />
                <div className="text-[11px] text-slate-500 leading-normal font-medium mt-1">
                  The time horizon to search backwards for invoices with the same Vendor and Total Amount to flag as potential duplicates.
                </div>
              </div>

              {/* AI Auto-Approval Confidence Slider */}
              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider">
                  <span className="text-slate-400">AI Min. Confidence Threshold</span>
                  <span className="text-primary font-black text-sm">{minConfidence}%</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="100"
                  step="1"
                  value={minConfidence}
                  onChange={(e) => setMinConfidence(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary focus:outline-none"
                />
                <div className="text-[11px] text-slate-500 leading-normal font-medium mt-1">
                  Invoices below this AI extraction confidence score will be forced into manual review regardless of rule results.
                </div>
              </div>
            </div>
          </motion.div>

          {/* Email Integration */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/2 filter blur-3xl pointer-events-none" />
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Mail className="w-4 h-4 text-primary" /> Automated Email Ingestion
              </h3>
              <button
                onClick={() => setEmailEnabled(!emailEnabled)}
                className={`w-12 h-6.5 rounded-full p-1 transition-all duration-300 ${
                  emailEnabled ? "bg-emerald-500 shadow-[0_0_12px_var(--color-emerald-500)]" : "bg-slate-800"
                }`}
              >
                <div 
                  className={`bg-white w-4.5 h-4.5 rounded-full shadow-md transform transition-transform duration-300 ${
                    emailEnabled ? "translate-x-5.5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
            
            <div className={`space-y-4 transition-all duration-500 ${emailEnabled ? "opacity-100" : "opacity-40 pointer-events-none"}`}>
              <div className="text-[11px] text-slate-400 leading-normal font-medium mb-4">
                Connect an AP inbox via IMAP. The system will automatically download attachments from new emails and route them through the AI pipeline.
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider ml-1">IMAP Server</label>
                  <input
                    type="text"
                    value={emailServer}
                    onChange={(e) => setEmailServer(e.target.value)}
                    placeholder="imap.gmail.com"
                    className="w-full h-11 px-4 bg-slate-950/50 border border-slate-850 rounded-xl text-sm font-medium text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-slate-600"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider ml-1">Account Email</label>
                  <input
                    type="email"
                    value={emailAddress}
                    onChange={(e) => setEmailAddress(e.target.value)}
                    placeholder="ap-invoices@company.com"
                    className="w-full h-11 px-4 bg-slate-950/50 border border-slate-850 rounded-xl text-sm font-medium text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-slate-600"
                  />
                </div>
                <div className="space-y-1.5 sm:col-span-2">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider ml-1">App Password</label>
                  <input
                    type="password"
                    value={emailPassword}
                    onChange={(e) => setEmailPassword(e.target.value)}
                    placeholder="••••••••••••••••"
                    className="w-full h-11 px-4 bg-slate-950/50 border border-slate-850 rounded-xl text-sm font-medium text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-slate-600"
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* ERP Integration */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
            className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/2 filter blur-3xl pointer-events-none" />
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Database className="w-4 h-4 text-primary" /> ERP Sync (Webhook)
              </h3>
              <button
                onClick={() => setErpEnabled(!erpEnabled)}
                className={`w-12 h-6.5 rounded-full p-1 transition-all duration-300 ${
                  erpEnabled ? "bg-primary shadow-[0_0_12px_var(--color-primary)]" : "bg-slate-800"
                }`}
              >
                <div 
                  className={`bg-white w-4.5 h-4.5 rounded-full shadow-md transform transition-transform duration-300 ${
                    erpEnabled ? "translate-x-5.5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
            
            <div className={`space-y-4 transition-all duration-500 ${erpEnabled ? "opacity-100" : "opacity-40 pointer-events-none"}`}>
              <div className="text-[11px] text-slate-400 leading-normal font-medium mb-4">
                Automatically push successfully APPROVED invoices to your core ERP system via a standard JSON webhook.
              </div>
              
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider ml-1">Destination Webhook URL</label>
                <div className="relative">
                  <LinkIcon className="absolute left-4 top-3.5 w-4 h-4 text-slate-500" />
                  <input
                    type="url"
                    value={erpWebhook}
                    onChange={(e) => setErpWebhook(e.target.value)}
                    placeholder="https://api.netsuite.com/rest/..."
                    className="w-full h-11 pl-11 pr-4 bg-slate-950/50 border border-slate-850 rounded-xl text-sm font-medium text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-slate-600"
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Form Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800/60 pb-8">
            <button
              onClick={handleReset}
              className="h-11 px-5 rounded-xl border border-slate-850 text-slate-300 text-sm font-semibold hover:bg-slate-900 transition-colors flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" /> Reset Defaults
            </button>
            <button
              onClick={handleSave}
              disabled={isPending}
              className="h-11 px-8 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-all shadow-lg hover:shadow-primary/20 flex items-center gap-2 disabled:opacity-55"
            >
              {isPending ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {isPending ? "Updating Configuration..." : "Apply Settings"}
            </button>
          </div>
        </div>

        {/* Right Side: Informational Widget (4 cols) */}
        <div className="md:col-span-4 space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
            className="bg-slate-900/10 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md flex flex-col gap-6 relative"
          >
            <div className="absolute top-0 right-0 w-full h-full bg-primary/2 filter blur-3xl pointer-events-none" />
            
            <div>
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-400 mb-2.5">Engine Strategy</h4>
              <p className="text-xs text-slate-350 leading-relaxed font-medium">
                These validation parameters are injected dynamically into the deterministic validation loops. When the rule matching processor runs, it queries this policy state on the fly.
              </p>
            </div>

            <div className="border-t border-slate-850/60 pt-5 space-y-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                <Clock className="w-4 h-4 text-slate-500 animate-pulse" />
                <span>Real-Time Configuration Refresh</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-normal font-medium">
                Changes applied are immediate. There is no need to restart the server processes or re-scaffold database tables.
              </p>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.25 }}
            className="bg-emerald-950/20 border border-emerald-900/30 rounded-2xl p-6 shadow-xl backdrop-blur-md"
          >
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-emerald-500 mb-2.5">Data Security</h4>
            <p className="text-[11px] text-slate-400 leading-normal font-medium">
              All credentials such as Email App Passwords and Webhook Secrets are encrypted at rest using AES-256 before being persisted to the secure configuration vault.
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
