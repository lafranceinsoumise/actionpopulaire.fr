import { useState } from "react";

export const useFilters = () => {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({});

  const switchFilters = () => {
    setShowFilters(!showFilters);
    if (Object.entries(filters).length) {
      setFilters({});
    }
  };

  return [showFilters, setShowFilters, filters, setFilters, switchFilters];
};
