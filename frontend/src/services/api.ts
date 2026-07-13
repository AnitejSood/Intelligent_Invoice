/* FinanceFlow AI — API Service Layer */

import axios from "axios";
import type {
  Invoice,
  DashboardMetrics,
  DashboardAnalytics,
  PaginatedResponse,
} from "@/types";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// ─── Dashboard ─────────────────────────────────────────────
export async function getDashboard(): Promise<DashboardMetrics> {
  const { data } = await api.get("/dashboard");
  return data.data;
}

export async function getDashboardAnalytics(): Promise<DashboardAnalytics> {
  const { data } = await api.get("/dashboard/analytics");
  return data.data;
}

// ─── Invoices ──────────────────────────────────────────────
export async function uploadInvoice(file: File): Promise<Invoice> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/invoices/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getInvoice(id: number): Promise<Invoice> {
  const { data } = await api.get(`/invoices/${id}`);
  return data.data ?? data;
}

export async function getInvoices(params?: {
  page?: number;
  limit?: number;
  search?: string;
  status?: string;
  type?: string;
}): Promise<PaginatedResponse<Invoice>> {
  const page = params?.page ?? 1;
  const limit = params?.limit ?? 15;
  const skip = (page - 1) * limit;
  
  const queryParams = {
    skip,
    limit,
    search: params?.search || undefined,
    status: params?.status || undefined,
  };
  
  const { data } = await api.get("/invoices", { params: queryParams });
  return data;
}

export async function reprocessInvoice(id: number): Promise<Invoice> {
  const { data } = await api.post(`/invoices/${id}/reprocess`);
  return data;
}

// ─── Settings ──────────────────────────────────────────────
export interface BusinessSettings {
  PO_TOLERANCE_PERCENT: number;
  MAX_INVOICE_AGE_DAYS: number;
  REQUIRE_GST: boolean;
  REQUIRE_PO: boolean;
  DUPLICATE_DETECTION_DAYS: number;
  MIN_CONFIDENCE_THRESHOLD: number;
  REQUIRE_LINE_ITEMS_MATCH: boolean;
  EMAIL_INGESTION_ENABLED: boolean;
  EMAIL_SERVER: string;
  EMAIL_ADDRESS: string;
  EMAIL_PASSWORD?: string;
  ERP_SYNC_ENABLED: boolean;
  ERP_WEBHOOK_URL: string;
}

export async function getBusinessSettings(): Promise<BusinessSettings> {
  const { data } = await api.get("/settings");
  return data.data;
}

export async function updateBusinessSettings(payload: BusinessSettings): Promise<BusinessSettings> {
  const { data } = await api.post("/settings", payload);
  return data.data;
}

// ─── Health ────────────────────────────────────────────────
export async function getHealthStatus() {
  const { data } = await api.get("/health");
  return data;
}

export default api;
