import PropTypes from "prop-types";
import React, { useState, useMemo, useCallback } from "react";
import styled from "styled-components";

import ActivityCard from "./ActivityCard";
import RequiredActionCard, { requiredActionTypes } from "./RequiredActionCard";

const StyledList = styled.ul`
  list-style: none;
  box-sizing: border-box;
  max-width: 100%;
  padding: 12px;
  background-color: ${({ type }) =>
    type === "required" ? "white" : "transparent"};
  box-shadow: ${({ type }) =>
    type === "required"
      ? "0px 0px 3px rgba(0, 35, 44, 0.1), 0px 3px 2px rgba(0, 35, 44, 0.05)"
      : "none"};

  h2 {
    box-sizing: border-box;
    padding: 0 10px;
    font-size: 20px;
    display: flex;
    align-items: center;
    margin-bottom: 13px;

    small {
      display: inline-flex;
      width: 27px;
      height: 27px;
      font-size: 13px;
      background-color: crimson;
      color: white;
      border-radius: 100%;
      align-items: center;
      justify-content: center;
    }
  }

  li {
    margin-bottom: 16px;
  }
`;

const ActivityList = (props) => {
  const { data, include } = props;

  const [dismissed, setDismissed] = useState([]);
  const handleDismiss = useCallback((id) => {
    // TODO: Actually update the activity status
    setDismissed((state) => [...state, id]);
  }, []);

  const [required, unrequired] = useMemo(() => {
    const required = [];
    const unrequired = [];
    if (Array.isArray(data) && data.length > 0) {
      data.forEach((activity) => {
        if (requiredActionTypes.includes(activity.type)) {
          include.includes("required") && required.push(activity);
        } else {
          include.includes("unrequired") && unrequired.push(activity);
        }
      });
    }
    return [required, unrequired];
  }, [data, include]);

  return (
    <article>
      {required.length > 0 ? (
        <StyledList type="required">
          <h2>
            <small>{required.length}</small>&ensp;À traiter
          </h2>
          {required.map((activity) =>
            dismissed.includes(activity.id) ? null : (
              <li key={activity.id}>
                <RequiredActionCard onDismiss={handleDismiss} {...activity} />
              </li>
            )
          )}
        </StyledList>
      ) : null}
      {unrequired.length > 0 ? (
        <StyledList type="unrequired">
          {unrequired.map(({ id, ...props }) => (
            <li key={id}>
              <ActivityCard {...props} />
            </li>
          ))}
        </StyledList>
      ) : null}
    </article>
  );
};
ActivityList.propTypes = {
  include: PropTypes.arrayOf(PropTypes.oneOf(["required", "unrequired"])),
  data: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.isRequired,
      type: PropTypes.string.isRequired,
    })
  ),
};
ActivityList.defaultProps = {
  include: ["required", "unrequired"],
};
export default ActivityList;
