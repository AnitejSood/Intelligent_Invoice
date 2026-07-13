import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { 
  Building2, Package, Search, AlertCircle, 
  CheckCircle2, Clock, Hash, FileText, Filter
} from "lucide-react";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { API_BASE_URL } from "@/services/api";

export default function VendorsPOsPage() {
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') || "";
  
  const [activeTab, setActiveTab] = useState<'pos' | 'vendors'>('pos');
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [statusFilter, setStatusFilter] = useState("ALL");

  const { data: posData, isLoading: isLoadingPOs } = useQuery({
    queryKey: ['purchase_orders'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/api/v1/purchase-orders?limit=100`);
      if (!res.ok) throw new Error('Failed to fetch POs');
      return res.json();
    }
  });

  const { data: vendorsData, isLoading: isLoadingVendors } = useQuery({
    queryKey: ['vendors'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/api/v1/vendors?limit=100`);
      if (!res.ok) throw new Error('Failed to fetch vendors');
      return res.json();
    }
  });

  const updateVendorStatus = useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }) => {
      const res = await fetch(`${API_BASE_URL}/api/v1/vendors/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      if (!res.ok) throw new Error('Failed to update status');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
    }
  });

  const getStatusBadge = (status: string) => {
    switch(status) {
      case "OPEN":
      case "ACTIVE":
      case "APPROVED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold bg-success/10 text-emerald-400 border border-success/20">
            <CheckCircle2 className="w-3 h-3" /> {status}
          </span>
        );
      case "CLOSED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold bg-slate-500/10 text-slate-400 border border-slate-500/20">
            <Clock className="w-3 h-3" /> CLOSED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertCircle className="w-3 h-3" /> {status}
          </span>
        );
    }
  };

  const filteredPOs = posData?.items?.filter((po: any) => {
    const matchesSearch = po.po_number.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          po.vendor?.vendor_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || po.status === statusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  const filteredVendors = vendorsData?.items?.filter((v: any) => {
    const matchesSearch = v.vendor_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || v.status === statusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  return (
    <div className="space-y-8">
      {/* Header & Tabs */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <Building2 className="w-8 h-8 text-primary" />
            Vendor Directory
          </h1>
          <p className="text-sm text-slate-400 mt-2 font-medium max-w-xl leading-relaxed">
            Manage approved vendors, active purchase orders, and track ledger capacities across your supply chain.
          </p>
        </div>

        <div className="flex bg-slate-900/60 border border-slate-800/80 p-1.5 rounded-2xl shadow-inner relative">
          <button
            onClick={() => { setActiveTab('pos'); setStatusFilter('ALL'); }}
            className={`relative z-10 flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
              activeTab === 'pos' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Package className="w-4 h-4" />
            Purchase Orders
          </button>
          <button
            onClick={() => { setActiveTab('vendors'); setStatusFilter('ALL'); }}
            className={`relative z-10 flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
              activeTab === 'vendors' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Building2 className="w-4 h-4" />
            Vendors
          </button>
          
          {/* Animated Tab Background Indicator */}
          <motion.div 
            layoutId="activeTabIndicator"
            className="absolute top-1.5 bottom-1.5 w-[165px] bg-slate-800 border border-slate-700/50 rounded-xl shadow-md"
            initial={false}
            animate={{ 
              x: activeTab === 'pos' ? 0 : 165
            }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
          />
        </div>
      </div>

      {/* Filters Area */}
      <div className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-md shadow-lg flex flex-col sm:flex-row items-center gap-4">
        <div className="relative flex-1 w-full max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <input 
            type="text" 
            placeholder={`Search ${activeTab === 'pos' ? 'POs or Vendors' : 'Vendors'}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-11 bg-slate-950/50 border border-slate-850 rounded-xl pl-12 pr-4 text-sm text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-slate-500 font-medium"
          />
        </div>
        
        <div className="relative flex items-center gap-2 ml-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="h-11 bg-slate-950/50 border border-slate-850 rounded-xl px-4 text-sm font-bold text-slate-300 focus:outline-none focus:border-primary/50 appearance-none pr-10 cursor-pointer hover:border-slate-700 transition-colors"
          >
            <option value="ALL">All Statuses</option>
            {activeTab === 'pos' ? (
              <>
                <option value="OPEN">OPEN</option>
                <option value="CLOSED">CLOSED</option>
                <option value="CANCELLED">CANCELLED</option>
              </>
            ) : (
              <>
                <option value="APPROVED">APPROVED</option>
                <option value="PENDING">PENDING</option>
                <option value="REJECTED">REJECTED</option>
                <option value="SUSPENDED">SUSPENDED</option>
              </>
            )}
          </select>
          {/* Custom Select Chevron */}
          <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>
      </div>

      {/* Purchase Orders View */}
      {activeTab === 'pos' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {isLoadingPOs ? (
            <div className="col-span-full h-64 flex items-center justify-center text-slate-400">Loading POs...</div>
          ) : filteredPOs.length === 0 ? (
            <div className="col-span-full h-64 flex items-center justify-center text-slate-500 text-sm font-medium">No purchase orders found.</div>
          ) : (
            filteredPOs.map((po: any, idx: number) => (
              <motion.div 
                key={po.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.05 }}
                className="bg-slate-900/40 border border-slate-800/60 rounded-2xl p-6 shadow-xl relative overflow-hidden group hover:bg-slate-800/40 transition-colors"
              >
                {po.status === 'CLOSED' && (
                  <div className="absolute inset-0 bg-slate-950/40 backdrop-grayscale pointer-events-none z-10" />
                )}
                <div className="flex justify-between items-start mb-4 relative z-20">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Hash className="w-4 h-4 text-primary" />
                      <h3 className="text-lg font-black text-white">{po.po_number}</h3>
                    </div>
                    <p className="text-xs text-slate-400 font-medium">
                      Issued {format(new Date(po.created_at), "MMM d, yyyy")}
                    </p>
                  </div>
                  {getStatusBadge(po.status)}
                </div>

                <div className="space-y-4 relative z-20">
                  <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/30 border border-slate-850/40">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Vendor</span>
                    <span className="text-sm font-bold text-slate-200">{po.vendor?.vendor_name || "Unknown"}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/30 border border-slate-850/40">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Value</span>
                    <span className="text-sm font-black text-primary">₹{po.amount?.toLocaleString()}</span>
                  </div>

                  {po.linked_invoices && po.linked_invoices.length > 0 && (
                    <div className="pt-2 border-t border-slate-850">
                      <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Linked Invoices</h4>
                      <div className="space-y-2">
                        {po.linked_invoices.map((inv: any) => (
                          <Link 
                            key={inv.id} 
                            to={`/invoice/${inv.id}`}
                            className="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-primary/50 transition-colors group/link"
                          >
                            <div className="flex items-center gap-2">
                              <FileText className="w-3.5 h-3.5 text-slate-400 group-hover/link:text-primary transition-colors" />
                              <span className="text-xs font-bold text-slate-300 group-hover/link:text-white transition-colors">
                                {inv.invoice_number}
                              </span>
                            </div>
                            <span className="text-[10px] font-mono text-slate-500">₹{inv.total?.toLocaleString()}</span>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}

      {/* Vendors View */}
      {activeTab === 'vendors' && (
        <div className="bg-slate-900/30 border border-slate-800/80 rounded-2xl shadow-xl overflow-hidden backdrop-blur-md">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-950/50 border-b border-slate-800">
                <th className="text-left text-xs font-bold text-slate-400 uppercase tracking-wider p-5">Vendor Entity</th>
                <th className="text-left text-xs font-bold text-slate-400 uppercase tracking-wider p-5">GST Number</th>
                <th className="text-left text-xs font-bold text-slate-400 uppercase tracking-wider p-5">Bank Account</th>
                <th className="text-right text-xs font-bold text-slate-400 uppercase tracking-wider p-5">Status</th>
              </tr>
            </thead>
            <tbody>
              {isLoadingVendors ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">Loading vendors...</td></tr>
              ) : filteredVendors.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-slate-500">No vendors found.</td></tr>
              ) : (
                filteredVendors.map((vendor: any) => (
                  <tr key={vendor.id} className="border-b border-slate-850/40 hover:bg-slate-900/50 transition-colors">
                    <td className="p-5 text-sm font-bold text-white flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                        <Building2 className="w-4 h-4 text-primary" />
                      </div>
                      {vendor.vendor_name}
                    </td>
                    <td className="p-5 text-sm text-slate-300 font-mono">{vendor.gst_number || "—"}</td>
                    <td className="p-5 text-sm text-slate-300 font-mono">{vendor.bank_account || "—"}</td>
                    <td className="p-5 text-right flex items-center justify-end gap-4 h-full">
                      {getStatusBadge(vendor.status)}
                      {/* Status Editor Dropdown */}
                      <div className="relative inline-block mt-0.5">
                        <select 
                          value={vendor.status}
                          onChange={(e) => updateVendorStatus.mutate({ id: vendor.id, status: e.target.value })}
                          className="opacity-0 absolute inset-0 w-full h-full cursor-pointer z-10"
                          title="Change Status"
                        >
                          <option value="APPROVED">APPROVED</option>
                          <option value="PENDING">PENDING</option>
                          <option value="REJECTED">REJECTED</option>
                          <option value="SUSPENDED">SUSPENDED</option>
                        </select>
                        <button className="text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition-colors relative z-0 pointer-events-none">
                          Edit
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
