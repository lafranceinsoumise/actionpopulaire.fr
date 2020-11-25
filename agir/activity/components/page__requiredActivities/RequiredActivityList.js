import React, { useState, useMemo, useEffect, useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { parseActivities } from "@agir/activity/common/helpers";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import Activities from "@agir/activity/common/Activities";

import Layout, {
  LayoutTitle,
  LayoutSubtitle,
} from "@agir/front/dashboardComponents/Layout";
import RequiredActionCard from "./RequiredActionCard";

const Page = styled.article`
  margin: 0;
`;

const Counter = styled.span`
  background-color: ${style.redNSP};
  color: ${style.white};
  font-size: 13px;
  height: 2em;
  width: 2em;
  border-radius: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  margin-right: 12px;

  @media (max-width: ${style.collapse}px) {
  }
`;

const RequiredActivityList = () => {
  const { activities, dispatch } = useGlobalContext();

  const [dismissed, setDismissed] = useState([]);
  const handleDismiss = useCallback((id) => {
    // TODO: Actually update the activity status
    setDismissed((state) => [...state, id]);
  }, []);

  const { required } = useMemo(() => parseActivities(activities, dismissed), [
    activities,
    dismissed,
  ]);

  useEffect(() => {
    dispatch({
      type: "update-required-action-activities",
      requiredActionActivities: required,
    });
  }, [dispatch, required]);

  return (
    <Layout active="required-activity">
      <Page>
        <LayoutTitle>
          {required.length ? <Counter>{required.length}</Counter> : null}À
          traiter
        </LayoutTitle>
        <LayoutSubtitle>
          L’actualité de vos groupes et de la France Insoumise
        </LayoutSubtitle>
        <Activities
          CardComponent={RequiredActionCard}
          activities={required}
          onDismiss={handleDismiss}
        />
      </Page>
    </Layout>
  );
};
export default RequiredActivityList;
