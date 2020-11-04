import PropTypes from "prop-types";
import React, { useState, useMemo, useEffect, useCallback } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import ActivityCard from "./ActivityCard";
import RequiredActionCard, { requiredActionTypes } from "./RequiredActionCard";

import { useGlobalContext } from "@agir/front/genericComponents/GobalContext";

const StyledText = styled.p`
  margin: 0;
  width: 100%;
  padding: 16px 0;
`;
const StyledList = styled.ul`
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

export const parseActivities = (
  data,
  dismissed = [],
  include = ["required", "unrequired"]
) => {
  const required = [];
  const unrequired = [];
  if (Array.isArray(data) && data.length > 0) {
    data.forEach((activity) => {
      if (dismissed.includes(activity.id)) {
        return;
      }
      if (requiredActionTypes.includes(activity.type)) {
        include.includes("required") && required.push(activity);
      } else {
        include.includes("unrequired") && unrequired.push(activity);
      }
    });
  }
  return [required, unrequired];
};

const ActivityList = (props) => {
  const { data, include } = props;
  const { dispatch } = useGlobalContext();

  const [dismissed, setDismissed] = useState([]);
  const handleDismiss = useCallback((id) => {
    // TODO: Actually update the activity status
    setDismissed((state) => [...state, id]);
  }, []);

  const [required, unrequired] = useMemo(
    () => parseActivities(data, dismissed, include),
    [data, include, dismissed]
  );

  useEffect(() => {
    dispatch({
      type: "update-required-action-activities",
      requiredActionActivities: required,
    });
  }, [dispatch, required]);

  return (
    <article>
      {required.length + unrequired.length === 0 ? (
        <StyledText>Vous n'avez pas de notifications !</StyledText>
      ) : null}
      {required.length > 0 ? (
        <StyledList type="required">
          <h2>À traiter</h2>
          <h4>Vos notifications qui requièrent une action de votre part</h4>
          {required.map((activity) => (
            <li key={activity.id}>
              <RequiredActionCard onDismiss={handleDismiss} {...activity} />
            </li>
          ))}
        </StyledList>
      ) : null}
      {unrequired.length > 0 ? (
        <StyledList type="unrequired">
          <h2>Mes autres notifications</h2>
          <h4>L’actualité de vos groupes et de la France Insoumise</h4>
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
