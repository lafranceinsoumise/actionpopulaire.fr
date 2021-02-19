import useSWR from "swr";

export const useIsOffline = () => {
  const { data, error, isValidating } = useSWR("/api/session");

  if (!data && !error && isValidating) return null;

  return !!error;
};
