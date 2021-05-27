import useSWR from "swr";

import logger from "@agir/lib/utils/logger";

import * as api from "@agir/groups/groupPage/api";

const log = logger(__filename);

const fetcher = async (url) => {
  const res = await fetch(url);
  if (!res.ok) {
    let error = new Error("An error occurred while fetching the data.");
    error.status = res.status;
    throw error;
  }
  return res.json();
};

export const useGroup = (groupPk) => {
  const { data, error } = useSWR(
    api.getGroupPageEndpoint("getGroup", { groupPk }),
    fetcher,
    {
      onErrorRetry: (error) => {
        if (error.status === 404) return;
      },
    }
  );
  log.debug("Group data", data);

  if (error?.status === 404 || error?.status === 410) return false;
  return data;
};

export const useGroupSuggestions = (group) => {
  const hasSuggestions = group && group.id;
  const { data, error } = useSWR(
    hasSuggestions
      ? api.getGroupPageEndpoint("getGroupSuggestions", { groupPk: group.id })
      : null
  );
  log.debug("Group suggestions", data);

  return hasSuggestions && !error ? data : [];
};
