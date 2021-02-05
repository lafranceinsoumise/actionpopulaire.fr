import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import CenteredLayout from "@agir/front/dashboardComponents/CenteredLayout";
import GroupMessage from "@agir/groups/groupPage/GroupMessage";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getBackLink } from "@agir/front/globalContext/reducers";

const StyledBlock = styled.div`
  max-width: 780px;
  margin: 0 auto;
  padding: 0;

  @media (max-width: ${style.collapse}px) {
    align-items: stretch;
  }
`;

const GroupMessagePage = (props) => {
  const backLink = useSelector(getBackLink);

  return (
    <CenteredLayout backLink={backLink} $maxWidth="780px">
      <StyledBlock>
        <GroupMessage {...props} />
      </StyledBlock>
    </CenteredLayout>
  );
};

export default GroupMessagePage;
