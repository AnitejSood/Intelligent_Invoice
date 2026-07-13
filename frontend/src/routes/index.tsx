/* FinanceFlow AI — Application Routes */
import { createBrowserRouter } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import DashboardPage from "@/pages/dashboard/DashboardPage";
import UploadPage from "@/pages/upload/UploadPage";
import HistoryPage from "@/pages/history/HistoryPage";
import InvoiceDetailsPage from "@/pages/invoice/InvoiceDetailsPage";
import SettingsPage from "@/pages/settings/SettingsPage";
import VendorsPOsPage from "@/pages/vendors/VendorsPOsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "upload", element: <UploadPage /> },
      { path: "history", element: <HistoryPage /> },
      { path: "invoice/:id", element: <InvoiceDetailsPage /> },
      { path: "vendors", element: <VendorsPOsPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
]);

