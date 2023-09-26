import PropTypes from "prop-types";
import React, { useState } from "react";

import SearchAndSelectField from "@agir/front/formComponents/SearchAndSelectField";

import { searchVotingLocation } from "@agir/elections/Common/api";
import { debounce } from "@agir/lib/utils/promises";

const VotingLocationField = (props) => {
  const { onChange, value, ...rest } = props;
  const [isLoading, setIsLoading] = useState(false);
  const [options, setOptions] = useState([]);

  const handleSearch = debounce(async (searchTerm) => {
    setIsLoading(true);
    setOptions(undefined);
    const { data, _error } = await searchVotingLocation(searchTerm);
    setIsLoading(false);
    const results = data.map((choice) => ({
      ...choice,
      icon: choice.type === "commune" ? "location-dot" : "globe:regular",
    }));
    setOptions(results);
    return results;
  }, 600);

  return (
    <SearchAndSelectField
      {...rest}
      minSearchTermLength={1}
      isLoading={isLoading}
      value={value}
      onChange={onChange}
      onSearch={handleSearch}
      defaultOptions={options}
      placeholder="Chercher par nom, code postal…"
    />
  );
};

VotingLocationField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.string,
};

export default VotingLocationField;
