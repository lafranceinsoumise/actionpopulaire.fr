import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import LocationItem from "./LocationItem";

const StyledItems = styled.ul`
  list-style: none;
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  padding: 0;
  margin: 0;

  & > strong {
    font-size: 1rem;
    font-weight: 600;
  }
`;

const LocationItems = (props) => {
  const { locations, name, onChange, disabled } = props;

  const haslocations = useMemo(
    () => Array.isArray(locations) && locations.length > 0,
    [locations]
  );

  if (!haslocations) {
    return null;
  }

  return (
    <StyledItems>
      <strong>Lieu</strong>
      {locations.map(({ id, ...locationData }) => (
        <li key={id}>
          <LocationItem
            onChange={onChange}
            disabled={disabled}
            name={name}
            locationData={locationData}
          />
        </li>
      ))}
    </StyledItems>
  );
};

LocationItems.propTypes = {
  name: PropTypes.string,
  locations: PropTypes.array,
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
};

export default LocationItems;
