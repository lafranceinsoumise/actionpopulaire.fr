import PropTypes from "prop-types";
import React from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import * as style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Map from "@agir/carte/common/Map";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

import eventCardDefaultBackground from "@agir/front/genericComponents/images/event-card-default-bg.svg";

const StyledMap = styled.div``;
const StyledBody = styled.div``;
const StyledCard = styled(Card)`
  padding: 0;
  max-width: 397px;
  border: 1px solid ${style.black100};
  box-shadow: none;
  cursor: pointer;
  overflow: hidden;
  border-radius: ${style.borderRadius};

  @media (max-width: ${style.collapse}px) {
    width: calc(100vw - 4rem);
    max-width: 294px;
    height: 360px;
  }

  ${StyledMap} {
    background-image: url(${eventCardDefaultBackground});
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-color: #fafafa;
    height: 216px;

    @media (max-width: ${style.collapse}px) {
      height: 159px;
    }

    img {
      height: 100%;
      width: auto;
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
  const { id, name, location, iconConfiguration, backLink } = props;
  const { city, zip, coordinates, staticMapUrl } = location || {};
  const history = useHistory();
  const handleClick = React.useCallback(() => {
    id &&
      routeConfig.groupDetails &&
      history.push(routeConfig.groupDetails.getLink({ groupPk: id }), {
        backLink,
      });
  }, [history, id, backLink]);

  return (
    <StyledCard onClick={handleClick}>
      <StyledMap>
        {Array.isArray(coordinates?.coordinates) && (
          <Map
            center={coordinates.coordinates}
            iconConfiguration={iconConfiguration}
            staticMapUrl={staticMapUrl}
            isStatic
          />
        )}
      </StyledMap>
      <StyledBody>
        <h4>{name}</h4>
        <p>
          {(zip || city) && <FeatherIcon name="map-pin" small inline />}
          &nbsp;
          {(zip || city) && <span>{`${zip} ${city}`.trim()}</span>}
        </p>
        <Button
          link
          route="groupDetails"
          routeParams={{ groupPk: id }}
          backLink={backLink}
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
    staticMapUrl: PropTypes.string,
  }),
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};
export default GroupSuggestionCard;
