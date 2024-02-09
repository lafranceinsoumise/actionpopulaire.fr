import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";

import axios from "@agir/lib/utils/axios";

import SearchAndSelectField, {
  useRemoteSearch,
} from "@agir/front/formComponents/SearchAndSelectField";

const COMMUNE_TYPE_LABEL = {
  COM: "",
  ARM: "",
  COMA: ", commune associée",
  COMD: ", commune déléguée",
  SRM: ", secteur électoral",
};

export const searchCommune = async (searchTerm, types) => {
  const result = {
    data: [],
    errors: null,
  };

  const url = "/data-france/communes/chercher/";

  const params = new URLSearchParams([
    ["q", searchTerm.trim()],
    ...types.map((t) => ["type", t]),
  ]);

  try {
    const response = await axios.get(url, {
      params,
      headers: { Accept: "application/json" },
    });
    result.data = response.data.results;
  } catch (e) {
    result.errors = (e.response && e.response.data) || { global: e.message };
  }
  return result;
};

const CommuneField = (props) => {
  const { onChange, value, types, ...rest } = props;

  const search = useCallback(
    (searchTerm) => searchCommune(searchTerm, types),
    [types],
  );

  const formatResults = useCallback((results) => {
    if (!Array.isArray(results) || results.length === 0) {
      return [];
    }
    return results.map((commune) => ({
      ...commune,
      id: commune.code,
      value: commune.code,
      label: [
        commune.nom,
        commune.code_departement,
        COMMUNE_TYPE_LABEL[commune.type],
      ]
        .filter(Boolean)
        .join(" · "),
    }));
  }, []);

  const [handleSearch, _options, isLoading] = useRemoteSearch(
    search,
    formatResults,
  );

  const currentValue = useMemo(() => {
    if (!value) {
      return value;
    }
    if (value.value && value.label) {
      return value;
    }
    return formatResults([value])[0];
  }, [value, formatResults]);

  return (
    <SearchAndSelectField
      placeholder="Chercher par nom, code …"
      {...rest}
      isLoading={isLoading}
      value={currentValue}
      onChange={onChange}
      onSearch={handleSearch}
      isClearable
    />
  );
};

CommuneField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.string,
  types: PropTypes.arrayOf(
    PropTypes.oneOf(["COM", "ARM", "COMA", "COMD", "SRM"]),
  ),
};

export default CommuneField;
