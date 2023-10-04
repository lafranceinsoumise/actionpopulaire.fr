import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";

import SearchAndSelectField, {
  useRemoteSearch,
} from "@agir/front/formComponents/SearchAndSelectField";

import { getOrganizedEvents } from "@agir/events/common/api";
import { displayHumanDateString } from "@agir/lib/utils/time";

const EventField = (props) => {
  const { onChange, value, groupPk, ...rest } = props;

  const search = useCallback(
    (searchTerm) =>
      getOrganizedEvents({ q: searchTerm, group: groupPk, include_past: 1 }),
    [groupPk],
  );

  const formatResults = useCallback((results) => {
    if (!Array.isArray(results) || results.length === 0) {
      return [];
    }
    return results.map((event) => ({
      ...event,
      value: event.id,
      label: [
        event.name,
        event.startTime ? displayHumanDateString(event.startTime) : null,
        event.location.shortLocation,
      ]
        .filter(Boolean)
        .join(" · "),
      icon: event?.subtype?.iconName || "calendar-days:light",
      iconColor: event?.subtype?.color,
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
      placeholder="Chercher par nom, lieu …"
      {...rest}
      isLoading={isLoading}
      value={currentValue}
      onChange={onChange}
      onSearch={handleSearch}
      defaultOptions
      isClearable
    />
  );
};

EventField.propTypes = {
  groupPk: PropTypes.string,
  value: PropTypes.any,
  onChange: PropTypes.func,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.string,
};

export default EventField;
