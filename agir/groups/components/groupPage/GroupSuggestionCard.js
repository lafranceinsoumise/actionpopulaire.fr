import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Map from "@agir/carte/common/Map";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledMap = styled.div``;
const StyledBody = styled.div``;
const StyledCard = styled(Card)`
  padding: 0;
  max-width: 397px;
  border: 1px solid ${style.black100};
  box-shadow: none;

  @media (max-width: ${style.collapse}px) {
    width: 294px;
  }

  ${StyledMap} {
    height: 216px;

    @media (max-width: ${style.collapse}px) {
      height: 159px;
    }
  }

  ${StyledBody} {
    display: flex;
    flex-flow: column nowrap;
    align-items: center;
    text-align: center;
    padding: 2.5rem 1.5rem;

    @media (max-width: ${style.collapse}px) {
      padding: 1.5rem;
    }

    h4 {
      font-size: 1rem;
      line-height: 1.5;
      font-weight: 700;
      margin: 0 0 0.5rem;
    }

    p {
      margin: 0 0 1rem;
      font-size: 0.875rem;
      color: ${style.black500};
      line-height: 1.5;
      font-weight: 400;
    }
  }
`;

const GroupSuggestionCard = (props) => {
  const {
    id,
    name,
    location: { city, zip, coordinates },
    iconConfiguration,
  } = props;

  return (
    <StyledCard>
      <StyledMap>
        <Map
          center={
            coordinates && Array.isArray(coordinates.coordinates)
              ? coordinates.coordinates
              : [0, 0]
          }
          iconConfiguration={iconConfiguration}
          isStatic
        />
      </StyledMap>
      <StyledBody>
        <h4>{name}</h4>
        <p>
          <FeatherIcon name="map-pin" small inline />
          &nbsp;
          {(zip || city) && (
            <span>{[zip, city].filter(Boolean).join(" ")}</span>
          )}
        </p>
        <Button
          as="Link"
          to={routeConfig.groupDetails.getLink({ groupPk: id })}
          small
          color="secondary"
        >
          Voir le groupe
        </Button>
      </StyledBody>
    </StyledCard>
  );
};

GroupSuggestionCard.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  iconConfiguration: PropTypes.object,
  location: PropTypes.shape({
    city: PropTypes.string.isRequired,
    zip: PropTypes.string.isRequired,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }).isRequired,
  }).isRequired,
};
export default GroupSuggestionCard;
