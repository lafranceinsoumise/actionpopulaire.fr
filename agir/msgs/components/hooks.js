import useSWR from "swr";

export const useUnreadMessageCount = () => {
  const { data: session } = useSWR("/api/session/");
  return session?.unreadMessageCount || 0;
};
