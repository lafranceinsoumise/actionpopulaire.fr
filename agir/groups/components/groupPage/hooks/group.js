import useSWR from "swr";

import logger from "@agir/lib/utils/logger";

import * as api from "@agir/groups/utils/api";
import { useIsOffline } from "@agir/front/offline/hooks";

const log = logger(__filename);

export const useGroup = (groupPk) => {
  const isOffline = useIsOffline();
  const { data, error } = useSWR(api.getGroupEndpoint("getGroup", { groupPk }));
  log.debug("Group data", data);

  if (
    error?.name === "NetworkError" ||
    [403, 404].includes(error?.response?.status) ||
    (isOffline && !data)
  )
    return false;

  return data;
};

export const useGroupSuggestions = (group) => {
  const hasSuggestions = group && group.id;
  const { data, error } = useSWR(
    hasSuggestions
      ? api.getGroupEndpoint("getGroupSuggestions", { groupPk: group.id })
      : null,
  );
  log.debug("Group suggestions", data);

  return hasSuggestions && !error ? data : [];
};
