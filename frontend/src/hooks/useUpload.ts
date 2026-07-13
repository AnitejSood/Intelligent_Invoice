/* Upload mutation hook */
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadInvoice } from "@/services/api";

export function useUpload() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: uploadInvoice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
