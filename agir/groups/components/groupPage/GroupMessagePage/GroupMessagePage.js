import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMessage from "@agir/groups/groupPage/GroupMessage";

const StyledBlock = styled.div`
  max-width: 780px;
  margin: 0 auto;
  padding: 0;

  @media (max-width: ${style.collapse}px) {
    align-items: stretch;
  }
`;

const GroupMessagePage = (props) => {
  return (
    <StyledBlock>
      <GroupMessage {...props} />
    </StyledBlock>
  );
};

export default GroupMessagePage;
