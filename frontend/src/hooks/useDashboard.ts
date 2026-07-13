/* Dashboard data hook */
import { useQuery } from "@tanstack/react-query";
import { getDashboard, getDashboardAnalytics } from "@/services/api";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboard,
    refetchInterval: 30000, // Refresh every 30s
  });
}

export function useDashboardAnalytics() {
  return useQuery({
    queryKey: ["dashboard-analytics"],
    queryFn: getDashboardAnalytics,
    refetchInterval: 30000,
  });
}
