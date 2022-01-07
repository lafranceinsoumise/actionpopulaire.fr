import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import SearchAndSelectField from "@agir/front/formComponents/SearchAndSelectField";

import { searchVotingLocation } from "@agir/voting_proxies/Common/api";
import { debounce } from "@agir/lib/utils/promises";

const VotingLocationField = (props) => {
  const { onChange, value, ...rest } = props;
  const [isLoading, setIsLoading] = useState(false);
  const [options, setOptions] = useState([]);

  const handleSearch = debounce(async (searchTerm) => {
    if (searchTerm.length < 3) {
      setOptions(null);
      return null;
    }
    setIsLoading(true);
    setOptions(undefined);
    const { data, error } = await searchVotingLocation(searchTerm);
    setIsLoading(false);
    const results = data.map((choice) => ({
      ...choice,
      value: choice.id,
      label: choice.name,
      icon: choice.type === "commune" ? "flag" : "globe",
    }));
    setOptions(results);
    return results;
  }, 600);

  return (
    <SearchAndSelectField
      {...rest}
      isLoading={isLoading}
      value={value}
      onChange={onChange}
      onSearch={handleSearch}
      defaultOptions={options}
      placeholder="Chercher par nom, code ou code postal"
    />
  );
};

VotingLocationField.propTypes = {
  value: PropTypes.any.isRequired,
  onChange: PropTypes.func.isRequired,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.string,
};

export default VotingLocationField;
