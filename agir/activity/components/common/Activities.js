import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

export const EmptyList = styled.p`
  margin: 0;
  width: 100%;
  padding: 16px 0;

  @media (max-width: ${style.collapse}px) {
    margin: 0 25px;
  }

  strong {
    color: ${style.primary500};
  }
`;

export const StyledList = styled.ul`
  list-style: none;
  max-width: 711px;
  margin: 0;
  width: 100%;
  padding: 16px 0;

  @media (max-width: ${style.collapse}px) {
    margin: 0 auto;
  }

  h2,
  h4 {
    margin: 0;
    @media (max-width: ${style.collapse}px) {
      margin: 0 25px;
    }
  }

  h2 {
    font-size: 18px;
    line-height: 1.5;
    @media (max-width: ${style.collapse}px) {
      font-size: 16px;
    }
  }

  h4 {
    font-size: 14px;
    font-weight: normal;
    margin-bottom: 20px;
    line-height: 1.5;
    @media (max-width: ${style.collapse}px) {
      margin-bottom: 15px;
    }
  }

  li {
    margin: 0 0 16px;
    @media (max-width: ${style.collapse}px) {
      margin: ${({ type }) => (type === "required" ? "0 12px 12px" : "16px 0")};
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
