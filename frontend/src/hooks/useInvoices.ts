/* Invoice data hooks */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getInvoice, getInvoices, reprocessInvoice } from "@/services/api";

export function useInvoices(params?: {
  page?: number;
  limit?: number;
  search?: string;
  status?: string;
  type?: string;
}) {
  return useQuery({
    queryKey: ["invoices", params],
    queryFn: () => getInvoices(params),
  });
}

export function useInvoice(id: number) {
  return useQuery({
    queryKey: ["invoice", id],
    queryFn: () => getInvoice(id),
    enabled: !!id,
  });
}

export function useReprocessInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: reprocessInvoice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
