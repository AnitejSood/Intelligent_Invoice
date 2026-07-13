/* FinanceFlow AI — TypeScript Type Definitions */

export type InvoiceStatus = "APPROVED" | "REJECTED" | "PENDING_MANUAL_REVIEW";
export type DocumentType = "DIGITAL" | "SCANNED";
export type RuleResultStatus = "PASS" | "FAIL" | "WARNING";
export type ProcessingStage = "Upload" | "Detection" | "OCR" | "Extraction" | "Validation" | "Decision" | "Save";

export interface Invoice {
  id: number;
  invoice_number: string | null;
  vendor_name: string | null;
  po_number: string | null;
  invoice_date: string | null;
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  currency: string;
  status: InvoiceStatus;
  document_type: DocumentType | null;
  extraction_confidence: number | null;
  processing_time_ms: number | null;
  explanation: string | null;
  file_path: string | null;
  extracted_data: string | null;
  created_at: string;
  line_items?: LineItem[];
  rule_results?: RuleResult[];
  processing_logs?: ProcessingLog[];
}

export interface LineItem {
  id: number;
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

export interface RuleResult {
  id: number;
  rule_name: string;
  result: RuleResultStatus;
  expected: string | null;
  actual: string | null;
  message: string | null;
  evaluated_at: string;
}

export interface ProcessingLog {
  id: number;
  stage: ProcessingStage;
  status: "STARTED" | "COMPLETED" | "FAILED";
  duration_ms: number | null;
  metadata_json: string | null;
  created_at: string;
}

export interface DashboardMetrics {
  total_invoices: number;
  approved: number;
  rejected: number;
  pending: number;
  avg_processing_time_ms: number;
  approval_rate: number;
  recent_invoices: Invoice[];
}

export interface DashboardAnalytics {
  approval_rate: number;
  processing_trend: { date: string; count: number; avg_time: number }[];
  invoice_types: { type: string; count: number }[];
  status_distribution: { status: string; count: number }[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  code?: string;
}

export interface Vendor {
  id: number;
  vendor_name: string;
  gst_number: string | null;
  status: string;
  created_at: string;
}

export interface PurchaseOrder {
  id: number;
  po_number: string;
  vendor_id: number;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
}
