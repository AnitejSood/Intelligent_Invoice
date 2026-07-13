/* Business Settings hook */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getBusinessSettings, updateBusinessSettings } from "@/services/api";
import { toast } from "sonner";

export function useSettings() {
  return useQuery({
    queryKey: ["settings"],
    queryFn: getBusinessSettings,
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateBusinessSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
      toast.success("AP Validation engine thresholds updated successfully");
    },
    onError: (error: any) => {
      toast.error("Failed to update validation thresholds");
      console.error(error);
    }
  });
}
