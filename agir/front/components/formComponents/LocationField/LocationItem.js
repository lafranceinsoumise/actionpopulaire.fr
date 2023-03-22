import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledItem = styled(Card)`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  gap: 0.75rem;
  color: ${(props) => props.theme.black500};
  cursor: ${(props) => (props.$disabled ? "not-allowed" : "pointer")};
  opacity: ${(props) => (props.$disabled ? 0.75 : 1)};
  padding: 0.5rem;

  & > * {
    flex: 0 0 auto;
    margin: 0;
    font-size: 0.8125rem;
  }

  & > p {
    flex: 1 1 auto;
    display: flex;
    flex-flow: column nowrap;

    strong {
      font-size: 0.875rem;
      color: ${(props) => props.theme.black1000};
      font-weight: 600;
    }
  }
`;

const LocationItem = (props) => {
  const { name, locationData, onChange, disabled } = props;

  const handleClick = useCallback(() => {
    onChange && onChange(name, locationData);
  }, [onChange, name, locationData]);

  if (!locationData) {
    return null;
  }

  return (
    <StyledItem $disabled={disabled} onClick={handleClick} bordered>
      <FeatherIcon name="clock" />
      <p>
        <strong>{locationData.name}</strong>
        <span>
          {locationData.address1}, {locationData.zip} {locationData.city}
        </span>
      </p>
      <Button small disabled={disabled} onClick={handleClick} color="choose">
        Choisir
      </Button>
    </StyledItem>
  );
};

LocationItem.propTypes = {
  name: PropTypes.string,
  locationData: PropTypes.shape({
    name: PropTypes.string,
    address1: PropTypes.string,
    address2: PropTypes.string,
    city: PropTypes.string,
    zip: PropTypes.string,
    country: PropTypes.string,
  }),
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
};

export default LocationItem;
