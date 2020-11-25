import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

export const EmptyList = styled.p`
  margin: 0;
  width: 100%;
  padding: 16px 0;

  @media (max-width: ${style.collapse}px) {
    padding: 16px 25px;
  }

  strong {
    color: ${style.black1000};
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
  const { activities, onDismiss, CardComponent } = props;
  return (
    <article>
      {activities.length > 0 ? (
        <StyledList type="activities">
          {activities.map((activity) => (
            <li key={activity.id}>
              <CardComponent onDismiss={onDismiss} {...activity} />
            </li>
          ))}
        </StyledList>
      ) : (
        <EmptyList>
          <strong>Vous n'avez pas de notifications !</strong>
        </EmptyList>
      )}
    </article>
  );
};
Activities.propTypes = {
  CardComponent: PropTypes.element.isRequired,
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
