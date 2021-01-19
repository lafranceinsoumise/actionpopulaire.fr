import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { getGroupTypeWithLocation } from "./utils";

import Map from "@agir/carte/common/Map";

const StyledMap = styled.div``;
const StyledBanner = styled.div`
  display: flex;
  flex-flow: row-reverse nowrap;
  background-color: ${style.secondary500};
  margin: 0 auto;

  @media (max-width: ${style.collapse}px) {
    max-width: 100%;
    flex-flow: column nowrap;
    background-color: white;
  }

  header {
    flex: 1 1 auto;
    padding: 2.25rem;

    @media (max-width: ${style.collapse}px) {
      padding: 1.5rem;
    }
  }

  h2,
  h4 {
    margin: 0;
    &::first-letter {
      text-transform: uppercase;
    }
  }

  h2 {
    font-weight: 700;
    font-size: 1.75rem;
    line-height: 1.419;
    margin-bottom: 0.5rem;

    @media (max-width: ${style.collapse}px) {
      font-size: 1.25rem;
      line-height: 1.519;
    }
  }

  h4 {
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.5;

    @media (max-width: ${style.collapse}px) {
      font-size: 0.875rem;
    }
  }

  ${StyledMap} {
    flex: 0 0 424px;
    clip-path: polygon(100% 0%, 100% 100%, 0% 100%, 11% 0%);

    @media (max-width: ${style.collapse}px) {
      clip-path: none;
      width: 100%;
      flex-basis: 155px;
    }
  }
`;

const GroupBanner = (props) => {
  const { name, type, location, commune, iconConfiguration } = props;

  const subtitle = useMemo(
    () => getGroupTypeWithLocation(type, location, commune),
    [type, location, commune]
  );

  return (
    <StyledBanner>
      {location.coordinates &&
      Array.isArray(location.coordinates.coordinates) ? (
        <StyledMap>
          <Map
            center={location.coordinates.coordinates}
            iconConfiguration={iconConfiguration}
            isStatic
          />
        </StyledMap>
      ) : null}
      <header>
        <h2>{name}</h2>
        <h4>{subtitle}</h4>
      </header>
    </StyledBanner>
  );
};
GroupBanner.propTypes = {
  name: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  iconConfiguration: PropTypes.object,
  location: PropTypes.shape({
    city: PropTypes.string,
    zip: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
  }).isRequired,
  commune: PropTypes.shape({
    nameOf: PropTypes.string,
  }),
};
export default GroupBanner;
