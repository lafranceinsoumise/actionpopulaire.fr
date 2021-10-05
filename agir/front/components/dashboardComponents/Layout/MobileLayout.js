import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Navigation from "@agir/front/dashboardComponents/Navigation";

const StyledContainer = styled.div`
  padding-top: 24px;
  padding-bottom: 24px;
  background-color: ${({ smallBackgroundColor }) =>
    smallBackgroundColor || "transparent"};
`;

const MobileLayout = (props) => {
  const { children } = props;

  return (
    <StyledContainer {...props}>
      <section>{children}</section>
      <Navigation {...props} />
    </StyledContainer>
  );
};

export default MobileLayout;

MobileLayout.propTypes = {
  children: PropTypes.node,
};
