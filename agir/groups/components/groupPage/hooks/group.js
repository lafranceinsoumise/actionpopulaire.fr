import useSWR from "swr";

import logger from "@agir/lib/utils/logger";

import * as api from "@agir/groups/groupPage/api";

const log = logger(__filename);

export const useGroup = (groupPk) => {
  const { data } = useSWR(api.getGroupPageEndpoint("getGroup", { groupPk }));
  log.debug("Group data", data);

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
