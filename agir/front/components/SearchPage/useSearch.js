import { useState, useEffect } from "react";

import { getSearch } from "./api.js";

export const useSearchResults = (search, type, filters) => {
  const [groups, setGroups] = useState([]);
  const [events, setEvents] = useState([]);
  const [errors, setErrors] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  let filtersValue = {};
  Object.entries(filters).map(([key, value]) => {
    let v;
    if (typeof value !== "object") {
      v = value;
    } else {
      v = value?.value;
    }
    filtersValue = { ...filtersValue, [key]: v };
  });

  useEffect(async () => {
    if (search.length < 3) {
      return;
    }
    setIsLoading(true);
    setErrors(null);
    const { data, error } = await getSearch({
      search,
      type,
      filters: filtersValue,
    });
    setIsLoading(false);
    if (error) {
      setErrors(error);
      return;
    }

    setGroups(data.groups);
    setEvents(data.events);
  }, [search, type, filters]);

  return [groups, events, errors, isLoading];
};
