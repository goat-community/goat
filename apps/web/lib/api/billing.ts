import useSWR from "swr";

import { fetcher } from "@/lib/api/fetcher";
import type { PlansList } from "@/lib/validations/billing";

export const BILLING_API_BASE_URL = new URL("api/v1/billing", process.env.NEXT_PUBLIC_ACCOUNTS_API_URL).href;

export const useAppPlans = () => {
  const { data, isLoading, error, mutate, isValidating } = useSWR<PlansList>(
    `${BILLING_API_BASE_URL}/plans`,
    fetcher
  );
  return {
    plans: data,
    isLoading: isLoading,
    isError: error,
    mutate,
    isValidating,
  };
};
