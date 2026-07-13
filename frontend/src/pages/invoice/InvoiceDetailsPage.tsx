import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { 
  ArrowLeft, CheckCircle2, AlertCircle, Clock, FileText, 
  Building2, Calendar, DollarSign, Sparkles, AlertTriangle, RotateCw,
  Timer, Zap, Cpu, Shield, Brain, Database, Upload, Search,
  ChevronRight, Package, Layers
} from "lucide-react";
import { format } from "date-fns";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { getInvoice, API_BASE_URL } from "@/services/api";

interface ProcessingLog {
  id: number;
  stage: string;
  status: string;
  duration_ms: number | null;
  metadata_json: string | null;
  created_at: string | null;
}

interface RuleResult {
  id: number;
  rule_name: string;
  result: string;
  message: string | null;
  expected: string | null;
  actual: string | null;
}

interface LineItem {
  id: number;
  description: string | null;
  quantity: number;
  unit_price: number;
  amount: number;
}

interface LinkedPO {
  id: number;
  po_number: string;
  amount: number;
  currency: string;
  status: string;
}

const STAGE_ICONS: Record<string, any> = {
  "File Upload": Upload,
  "Document Detection & OCR": Cpu,
  "AI Semantic Extraction": Brain,
  "Context Lookup": Search,
  "Rule Engine Evaluation": Shield,
  "Decision Engine": Zap,
  "AI Explanation": Sparkles,
  "Database Persist": Database,
};

export default function InvoiceDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: invoice, isLoading, refetch } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => getInvoice(Number(id))
  });

  const fileUrl = invoice?.file_path 
    ? `${API_BASE_URL}/` + invoice.file_path.replace(/\\/g, "/")
    : null;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[500px] text-muted-foreground gap-4">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-medium tracking-wide">Syncing extraction audits...</span>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px] text-slate-400 gap-3 border border-dashed border-slate-800 rounded-2xl">
        <AlertTriangle className="w-10 h-10 text-rose-500 animate-bounce" />
        <p className="font-bold text-lg text-white">Document Not Located</p>
        <p className="text-sm text-slate-400">Please check the ledger logs or verify the id.</p>
        <Link to="/history" className="h-10 px-5 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 mt-2 flex items-center justify-center">
          Return to History
        </Link>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch(status) {
      case "APPROVED":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-success/10 text-success border border-success/30 glow-success">
            <CheckCircle2 className="w-4 h-4"/> APPROVED
          </span>
        );
      case "REJECTED":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-destructive/10 text-destructive border border-destructive/30 glow-destructive">
            <AlertCircle className="w-4 h-4"/> REJECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-warning/10 text-warning border border-warning/30">
            <Clock className="w-4 h-4"/> PENDING REVIEW
          </span>
        );
    }
  };

  const getRuleBadge = (result: string) => {
    return result === "PASS" ? (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-bold bg-success/10 text-emerald-400 border border-success/20">
        <CheckCircle2 className="w-3 h-3" /> PASS
      </span>
    ) : (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-bold bg-destructive/10 text-rose-400 border border-destructive/20">
        <AlertCircle className="w-3 h-3" /> FAIL
      </span>
    );
  };

  const totalPipelineMs = invoice.processing_logs?.reduce(
    (sum: number, l: ProcessingLog) => sum + (l.duration_ms || 0), 0
  ) || invoice.processing_time_ms || 0;

  const passCount = invoice.rule_results?.filter((r: RuleResult) => r.result === "PASS").length || 0;
  const failCount = invoice.rule_results?.filter((r: RuleResult) => r.result === "FAIL").length || 0;

  return (
    <div className="space-y-8">
      {/* Back button & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link to="/history" className="p-3 bg-slate-900/40 border border-slate-800/80 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-all shadow-md">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-black text-white tracking-tight">Invoice {invoice.invoice_number}</h2>
              {getStatusBadge(invoice.status)}
            </div>
            <p className="text-xs text-slate-400 mt-1 font-semibold">
              Processed on {invoice.created_at ? format(new Date(invoice.created_at), "PPP 'at' p") : "N/A"}
              {totalPipelineMs > 0 && (
                <span className="ml-2 text-primary">
                  • Pipeline: {(totalPipelineMs / 1000).toFixed(1)}s
                </span>
              )}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2">
            <span className="px-3 py-1.5 rounded-lg text-[10px] font-bold bg-slate-900/60 border border-slate-800 text-slate-300">
              {invoice.document_type || "UNKNOWN"}
            </span>
            <span className="px-3 py-1.5 rounded-lg text-[10px] font-bold bg-slate-900/60 border border-slate-800 text-slate-300">
              {((invoice.extraction_confidence || 0) * 100).toFixed(0)}% Confidence
            </span>
            <span className="px-3 py-1.5 rounded-lg text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              {passCount} Pass
            </span>
            {failCount > 0 && (
              <span className="px-3 py-1.5 rounded-lg text-[10px] font-bold bg-rose-500/10 border border-rose-500/20 text-rose-400">
                {failCount} Fail
              </span>
            )}
          </div>
          <button 
            onClick={() => {
              fetch(`/api/v1/invoices/${id}/reprocess`, { method: 'POST' })
                .then(() => refetch());
            }}
            className="flex items-center gap-2 px-5 h-11 bg-slate-900/40 border border-slate-800/80 hover:bg-slate-800 rounded-xl text-sm font-semibold text-slate-200 hover:text-white transition-all shadow-md"
          >
            <RotateCw className="w-4 h-4" />
            Trigger Audit
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* ──────────────── LEFT COLUMN (PDF + Schema + Linked POs) ──────────────── */}
        <div className="lg:col-span-5 flex flex-col gap-6 sticky top-6 max-h-[calc(100vh-3rem)] overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none'] pb-6">
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="bg-slate-900/30 border border-slate-800/80 rounded-2xl shadow-xl overflow-hidden flex flex-col h-[700px] shrink-0 backdrop-blur-md"
          >
            <div className="p-5 border-b border-slate-850 flex justify-between items-center bg-slate-950/20 shrink-0">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <FileText className="w-4.5 h-4.5 text-primary" />
                Document Vault
              </h3>
              <span className="text-[10px] uppercase font-bold tracking-wider bg-primary/10 text-primary border border-primary/20 px-2.5 py-1 rounded-lg">
                {invoice.document_type}
              </span>
            </div>
            <div className="flex-1 bg-slate-950/30 p-5 overflow-hidden">
              {fileUrl ? (
                <iframe 
                  src={fileUrl} 
                  className="w-full h-full rounded-xl border border-slate-850 bg-slate-900/10" 
                  title="Document Preview"
                />
              ) : (
                <div className="w-full h-full bg-slate-900/20 border border-slate-850 rounded-xl shadow-inner flex items-center justify-center text-slate-400 flex-col gap-3 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/1 to-transparent opacity-50 pointer-events-none" />
                  <FileText className="w-14 h-14 opacity-20 text-primary animate-pulse" />
                  <p className="text-xs font-bold tracking-wide uppercase text-slate-400">PDF Reader Container</p>
                  <p className="text-[10px] text-slate-500 font-medium text-center px-4 leading-normal">
                    No document path defined
                  </p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Extracted Schema Fields */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="bg-slate-900/30 border border-slate-800/80 rounded-2xl shadow-xl p-6 backdrop-blur-md relative shrink-0"
          >
            <div className="absolute top-0 left-0 w-full h-full bg-primary/2 filter blur-3xl pointer-events-none" />
            <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 mb-5">Extracted Schema Fields</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl border border-slate-850/60 bg-slate-950/20">
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                  <Building2 className="w-3.5 h-3.5 text-primary" /> Vendor
                </div>
                <div className="font-bold text-white text-sm truncate">{invoice.vendor_name || "Unmatched"}</div>
              </div>
              <div className="p-4 rounded-xl border border-slate-850/60 bg-slate-950/20">
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                  <Package className="w-3.5 h-3.5 text-primary" /> PO Number
                </div>
                <div className="font-bold text-white text-sm truncate">{invoice.po_number || "None"}</div>
              </div>
              <div className="p-4 rounded-xl border border-slate-850/60 bg-slate-950/20">
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                  <Calendar className="w-3.5 h-3.5 text-primary" /> Date
                </div>
                <div className="font-bold text-white text-sm truncate">
                  {invoice.invoice_date ? format(new Date(invoice.invoice_date), "MMM d, yyyy") : "N/A"}
                </div>
              </div>
              <div className="p-4 rounded-xl border border-slate-850/60 bg-slate-950/20">
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                  <DollarSign className="w-3.5 h-3.5 text-primary" /> Total
                </div>
                <div className="font-black text-lg text-primary truncate">₹{invoice.total?.toLocaleString()}</div>
              </div>
            </div>
            
            <div className="mt-5 pt-4 border-t border-slate-850/60 space-y-2">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-400">Subtotal</span>
                <span className="text-slate-200">₹{invoice.subtotal?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-400">Tax (GST)</span>
                <span className="text-slate-200">₹{invoice.tax?.toLocaleString()}</span>
              </div>
            </div>

            {/* Linked POs */}
            {invoice.linked_pos && invoice.linked_pos.length > 0 && (
              <div className="mt-5 pt-4 border-t border-slate-850/60">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
                  <Layers className="w-3.5 h-3.5 text-primary" />
                  Linked Purchase Orders
                </h4>
                <div className="space-y-2">
                  {invoice.linked_pos.map((po: LinkedPO) => (
                    <div 
                      key={po.id} 
                      onClick={() => navigate(`/vendors?search=${encodeURIComponent(po.po_number)}`)}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-950/40 border border-slate-850/60 hover:bg-slate-900/60 hover:border-primary/30 transition-all cursor-pointer group"
                    >
                      <div className="flex items-center gap-2">
                        <ChevronRight className="w-3.5 h-3.5 text-primary group-hover:translate-x-0.5 transition-transform" />
                        <span className="text-xs font-bold text-white">{po.po_number}</span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                          po.status === "OPEN" ? "bg-emerald-500/10 text-emerald-400" :
                          po.status === "CLOSED" ? "bg-slate-500/10 text-slate-400" :
                          "bg-rose-500/10 text-rose-400"
                        }`}>{po.status}</span>
                      </div>
                      <span className="text-xs font-bold text-slate-300">₹{po.amount?.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* ──────────────── RIGHT COLUMN (Audit, Line Items, Rules) ──────────────── */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* AI Copilot Explanation */}
          {invoice.explanation && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className={`p-6 rounded-2xl border flex flex-col gap-4 shadow-xl relative overflow-hidden backdrop-blur-md shrink-0 ${
                invoice.status === 'APPROVED' ? 'bg-success/5 border-success/15' : 
                invoice.status === 'REJECTED' ? 'bg-destructive/5 border-destructive/15' : 
                'bg-warning/5 border-warning/15'
              }`}
            >
              <div className="absolute top-0 right-0 w-48 h-48 bg-current/2 filter blur-3xl pointer-events-none" />
              <div className="flex items-center gap-3 mb-2">
                <div className="shrink-0 p-2.5 bg-slate-950/50 rounded-xl border border-white/5">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>
                <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">AI Copilot Assessment</h4>
              </div>
              <div className="text-sm text-slate-300 leading-relaxed font-medium markdown-body">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    strong: ({node, ...props}) => <strong className="text-white font-bold" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 mt-2 mb-3 space-y-1.5 marker:text-primary" {...props} />,
                    li: ({node, ...props}) => <li className="pl-1" {...props} />,
                    p: ({node, ...props}) => <p className="mb-3 last:mb-0" {...props} />,
                    h1: ({node, ...props}) => <h1 className="text-lg font-bold text-white mb-2 mt-4" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-base font-bold text-white mb-2 mt-3 border-b border-slate-800 pb-1" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-sm font-bold text-white mb-2 mt-3" {...props} />,
                    code: ({node, ...props}) => <code className="bg-slate-900/50 px-1.5 py-0.5 rounded font-mono text-xs text-primary" {...props} />,
                  }}
                >
                  {invoice.explanation}
                </ReactMarkdown>
              </div>
            </motion.div>
          )}

          {/* ───── Line Items Table ───── */}
          {invoice.line_items && invoice.line_items.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.15 }}
              className="bg-slate-900/30 border border-slate-800/80 rounded-2xl shadow-xl p-6 backdrop-blur-md shrink-0"
            >
              <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 mb-5 flex items-center gap-2">
                <Layers className="w-4 h-4 text-primary" />
                Extracted Line Items ({invoice.line_items.length})
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-800">
                      <th className="text-left text-[10px] font-bold text-slate-500 uppercase tracking-wider pb-3 pr-4">Description</th>
                      <th className="text-right text-[10px] font-bold text-slate-500 uppercase tracking-wider pb-3 px-4">Qty</th>
                      <th className="text-right text-[10px] font-bold text-slate-500 uppercase tracking-wider pb-3 px-4">Unit Price</th>
                      <th className="text-right text-[10px] font-bold text-slate-500 uppercase tracking-wider pb-3 pl-4">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoice.line_items.map((item: LineItem) => (
                      <tr key={item.id} className="border-b border-slate-850/40 hover:bg-slate-900/30 transition-colors">
                        <td className="py-3 pr-4 text-xs font-medium text-white">{item.description || "—"}</td>
                        <td className="py-3 px-4 text-xs text-slate-300 text-right font-mono">{item.quantity}</td>
                        <td className="py-3 px-4 text-xs text-slate-300 text-right font-mono">₹{item.unit_price?.toLocaleString()}</td>
                        <td className="py-3 pl-4 text-xs text-white text-right font-bold font-mono">₹{item.amount?.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colSpan={3} className="pt-3 text-xs font-bold text-slate-400 text-right pr-4">Subtotal</td>
                      <td className="pt-3 text-xs font-black text-primary text-right font-mono pl-4">
                        ₹{invoice.line_items.reduce((sum: number, i: LineItem) => sum + i.amount, 0).toLocaleString()}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </motion.div>
          )}

          {/* ───── Processing Timeline ───── */}
          {invoice.processing_logs && invoice.processing_logs.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.05 }}
              className="bg-slate-900/30 border border-slate-800/80 rounded-2xl shadow-xl p-6 backdrop-blur-md shrink-0"
            >
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Timer className="w-4 h-4 text-primary" />
                  Processing Timeline
                </h3>
                <span className="text-[10px] font-bold text-primary bg-primary/10 border border-primary/20 px-2.5 py-1 rounded-lg">
                  {(totalPipelineMs / 1000).toFixed(2)}s total
                </span>
              </div>
              
              <div className="space-y-1">
                {invoice.processing_logs.map((log: ProcessingLog, idx: number) => {
                  const StageIcon = STAGE_ICONS[log.stage] || Zap;
                  const durationMs = log.duration_ms || 0;
                  const pct = totalPipelineMs > 0 ? (durationMs / totalPipelineMs) * 100 : 0;
                  
                  let metadata: Record<string, any> = {};
                  try {
                    if (log.metadata_json) metadata = JSON.parse(log.metadata_json);
                  } catch {}
                  
                  // Key findings from metadata
                  const findings: string[] = [];
                  if (metadata.document_type) findings.push(`Type: ${metadata.document_type}`);
                  if (metadata.characters_extracted) findings.push(`${metadata.characters_extracted} chars`);
                  if (metadata.extraction_confidence !== undefined) findings.push(`${(metadata.extraction_confidence * 100).toFixed(0)}% confidence`);
                  if (metadata.fields_extracted) findings.push(`${metadata.fields_extracted} fields`);
                  if (metadata.line_items_count !== undefined) findings.push(`${metadata.line_items_count} items`);
                  if (metadata.po_count !== undefined) findings.push(`${metadata.po_count} PO(s) matched`);
                  if (metadata.passed !== undefined) findings.push(`${metadata.passed}✓ ${metadata.failed}✗`);
                  if (metadata.decision) findings.push(metadata.decision);
                  
                  return (
                    <div key={log.id || idx} className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-900/40 transition-colors group">
                      <div className="shrink-0 w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                        <StageIcon className="w-4 h-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-white">{log.stage}</span>
                          <span className="text-[10px] font-mono font-bold text-slate-400">
                            {durationMs >= 1000 ? `${(durationMs / 1000).toFixed(2)}s` : `${durationMs}ms`}
                          </span>
                        </div>
                        {/* Duration bar */}
                        <div className="mt-1.5 h-1 bg-slate-800 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${Math.max(pct, 2)}%` }}
                            transition={{ duration: 0.6, delay: idx * 0.1 }}
                            className="h-full bg-gradient-to-r from-primary/60 to-primary rounded-full"
                          />
                        </div>
                        {/* Findings chips */}
                        {findings.length > 0 && (
                          <div className="mt-1.5 flex flex-wrap gap-1">
                            {findings.map((f, i) => (
                              <span key={i} className="text-[9px] font-semibold text-slate-500 bg-slate-900/50 px-1.5 py-0.5 rounded">
                                {f}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}

          {/* ───── Rule Evaluations ───── */}
          {invoice.rule_results && invoice.rule_results.length > 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="bg-slate-900/30 border border-slate-800/80 rounded-2xl shadow-xl p-6 backdrop-blur-md shrink-0"
            >
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-primary" />
                  Deterministic Policy Verification
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-lg">
                    {passCount} Pass
                  </span>
                  {failCount > 0 && (
                    <span className="text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded-lg">
                      {failCount} Fail
                    </span>
                  )}
                </div>
              </div>
              <div className="space-y-3">
                {invoice.rule_results.map((rule: RuleResult) => (
                  <div key={rule.id} className={`p-4 rounded-xl border transition-colors ${
                    rule.result === "PASS" 
                      ? "border-slate-850/60 bg-slate-950/10 hover:bg-slate-950/20" 
                      : "border-rose-500/15 bg-rose-500/5 hover:bg-rose-500/8"
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs font-bold text-white uppercase tracking-wider">{rule.rule_name}</div>
                      <div>{getRuleBadge(rule.result)}</div>
                    </div>
                    <div className="text-[11px] text-slate-400 leading-normal font-medium mb-2">{rule.message}</div>
                    {(rule.expected || rule.actual) && (
                      <div className="grid grid-cols-2 gap-3 mt-2 pt-2 border-t border-slate-850/40">
                        <div>
                          <span className="text-[9px] font-bold text-slate-600 uppercase tracking-wider">Expected</span>
                          <p className="text-[11px] text-slate-300 font-mono mt-0.5 break-all">{rule.expected || "—"}</p>
                        </div>
                        <div>
                          <span className="text-[9px] font-bold text-slate-600 uppercase tracking-wider">Actual</span>
                          <p className={`text-[11px] font-mono mt-0.5 break-all ${
                            rule.result === "PASS" ? "text-emerald-400" : "text-rose-400"
                          }`}>{rule.actual || "—"}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          )}

        </div>
      </div>
    </div>
  );
}
