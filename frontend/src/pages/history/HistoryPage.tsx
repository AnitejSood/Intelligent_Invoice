import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useInvoices } from "@/hooks/useInvoices";
import { format } from "date-fns";
import { Search, Eye, AlertCircle, CheckCircle2, Clock, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading } = useInvoices({ 
    page, 
    limit: 15,
    search: debouncedSearch || undefined,
    status: status || undefined
  });

  const getStatusBadge = (status: string) => {
    switch(status) {
      case "APPROVED":
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold bg-success/10 text-emerald-400 border border-success/35 glow-success"><CheckCircle2 className="w-3.5 h-3.5"/> Approved</span>;
      case "REJECTED":
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold bg-destructive/10 text-rose-400 border border-destructive/35 glow-destructive"><AlertCircle className="w-3.5 h-3.5"/> Rejected</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold bg-warning/10 text-amber-400 border border-warning/35"><Clock className="w-3.5 h-3.5"/> Pending Audit</span>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
            Invoice Ledger
          </h2>
          <p className="text-sm text-slate-400 mt-1.5 flex items-center gap-1.5 font-medium">
            <Sparkles className="w-4 h-4 text-primary animate-pulse" />
            Consolidated history of OCR and AI processed transactions
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search ledger..."
              className="h-11 pl-10 pr-4 rounded-xl border border-slate-850 bg-slate-900/30 text-sm text-white outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/30 transition-all w-full sm:w-64"
            />
          </div>
          
          <div className="relative">
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                setPage(1);
              }}
              className="h-11 px-4 pr-8 rounded-xl border border-slate-850 bg-slate-900/30 text-sm text-slate-300 hover:text-white outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/30 transition-all cursor-pointer appearance-none min-w-[150px]"
            >
              <option value="" className="bg-slate-950 text-slate-300">All Statuses</option>
              <option value="APPROVED" className="bg-slate-950 text-emerald-400 font-bold">Approved</option>
              <option value="REJECTED" className="bg-slate-950 text-rose-400 font-bold">Rejected</option>
              <option value="PENDING_MANUAL_REVIEW" className="bg-slate-950 text-amber-400 font-bold">Pending Audit</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2050/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
            </div>
          </div>
        </div>
      </div>

      {/* Table Card */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-slate-900/30 border border-slate-800/80 rounded-2xl shadow-xl overflow-hidden backdrop-blur-md relative"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/1 filter blur-3xl pointer-events-none" />
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left border-collapse">
            <thead className="bg-slate-950/40 text-slate-400 font-semibold border-b border-slate-850">
              <tr>
                <th className="px-6 py-4.5 font-semibold text-xs uppercase tracking-wider">Invoice #</th>
                <th className="px-6 py-4.5 font-semibold text-xs uppercase tracking-wider">Vendor Entity</th>
                <th className="px-6 py-4.5 font-semibold text-xs uppercase tracking-wider">Doc Type</th>
                <th className="px-6 py-4.5 font-semibold text-xs uppercase tracking-wider text-right">Ledger Value</th>
                <th className="px-6 py-4.5 font-semibold text-xs uppercase tracking-wider">Audit Status</th>
                <th className="px-6 py-4.5 font-semibold text-xs uppercase tracking-wider">Processed Timestamp</th>
                <th className="px-6 py-4.5 font-semibold text-xs uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850/60 bg-transparent">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400 font-medium">
                    <div className="flex items-center justify-center gap-3">
                      <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                      Loading transactional data...
                    </div>
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500 font-medium">
                    No transactions matching parameters found.
                  </td>
                </tr>
              ) : (
                data?.items?.map((invoice, idx) => (
                  <motion.tr 
                    key={invoice.id} 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: idx * 0.02 }}
                    className="hover:bg-slate-900/30 transition-all border-slate-850/60"
                  >
                    <td className="px-6 py-4 font-bold text-white tracking-wide">{invoice.invoice_number}</td>
                    <td className="px-6 py-4 font-semibold text-slate-200">{invoice.vendor_name || "Unmatched Vendor"}</td>
                    <td className="px-6 py-4 text-xs font-bold text-slate-500 tracking-wider uppercase">{invoice.document_type}</td>
                    <td className="px-6 py-4 text-right font-black text-white">₹{invoice.total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4">{getStatusBadge(invoice.status)}</td>
                    <td className="px-6 py-4 text-slate-400 font-semibold text-xs">
                      {invoice.created_at ? format(new Date(invoice.created_at), "MMM d, yyyy HH:mm") : "-"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link 
                        to={`/invoice/${invoice.id}`}
                        className="inline-flex items-center justify-center w-9 h-9 rounded-xl border border-slate-850 bg-slate-950/20 hover:bg-slate-800 text-slate-400 hover:text-white transition-all shadow-sm"
                      >
                        <Eye className="w-4.5 h-4.5" />
                      </Link>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-850 bg-slate-950/20">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
            Showing <span className="text-white font-bold">{data?.items?.length || 0}</span> of <span className="text-white font-bold">{data?.total || 0}</span> transactions
          </span>
          <div className="flex items-center gap-2">
            <button 
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="h-9 px-4 rounded-xl border border-slate-850 bg-slate-950/20 text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-950/20 disabled:hover:text-slate-300 transition-all shadow-sm"
            >
              Previous
            </button>
            <button 
              disabled={!data || data.page * data.limit >= data.total}
              onClick={() => setPage(p => p + 1)}
              className="h-9 px-4 rounded-xl border border-slate-850 bg-slate-950/20 text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-950/20 disabled:hover:text-slate-300 transition-all shadow-sm"
            >
              Next
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
