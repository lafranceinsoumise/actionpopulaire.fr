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
  const { data } = props;

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
          required.push(activity);
        } else {
          unrequired.push(activity);
        }
      });
    }
    return [required, unrequired];
  }, [data]);

  return (
    <div>
      <StyledList>
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
      <StyledList>
        {unrequired.map(({ id, ...props }) => (
          <li key={id}>
            <ActivityCard {...props} />
          </li>
        ))}
      </StyledList>
    </div>
  );
};
ActivityList.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.isRequired,
      type: PropTypes.string.isRequired,
    })
  ),
};
export default ActivityList;
