import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import sunIcon from "./sunIcon.svg";

export const EmptyList = styled.p`
  margin: 0;
  padding: 32px 24px;
  display: flex;
  flex-flow: row nowrap;
  align-items: stretch;
  border: 1px solid ${style.black100};
  margin: 32px 0;

  @media (max-width: ${style.collapse}px) {
    margin: 24px 16px;
  }

  &::before {
    content: "";
    display: block;
    background-repeat: no-repeat;
    background-position: center left;
    background-size: contain;
    background-image: url(${sunIcon});
    flex: 0 0 50px;
    margin-right: 22px;
  }

  span {
    margin: 0;
    padding: 0;
    flex: 1 1 auto;
  }
`;

export const StyledList = styled.ul`
  list-style: none;
  max-width: 711px;
  margin: 0;
  width: 100%;
  padding: 1.5rem 0;

  @media (max-width: ${style.collapse}px) {
    padding: 0.5rem 0;
    margin: 0 auto;
    max-width: 100%;
  }

  li {
    margin: 0 0 16px;

    @media (max-width: ${style.collapse}px) {
      margin: 16px 0;
    }
  }
`;

export const Activities = (props) => {
  const { activities, routes, onDismiss, CardComponent } = props;
  return (
    <article>
      {activities.length > 0 ? (
        <StyledList type="activities">
          {activities.map((activity) => (
            <li key={activity.id}>
              <CardComponent
                onDismiss={onDismiss}
                routes={routes}
                {...activity}
              />
            </li>
          ))}
        </StyledList>
      ) : (
        <EmptyList>
          <span>
            Vous n’avez pas encore reçu d’actualités.
            <br />
            Revenez plus tard !
          </span>
        </EmptyList>
      )}
    </article>
  );
};
Activities.propTypes = {
  CardComponent: PropTypes.elementType.isRequired,
  routes: PropTypes.object,
  activities: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.isRequired,
      type: PropTypes.string.isRequired,
    })
  ),
  onDismiss: PropTypes.func,
};
Activities.defaultProps = {
  activities: [],
};
export default Activities;
