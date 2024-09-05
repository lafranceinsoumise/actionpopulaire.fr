import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import BottomBar from "@agir/front/app/Navigation/BottomBar";

const StyledContainer = styled.div`
  padding-top: 24px;
  padding-bottom: 24px;
  background-color: ${(props) =>
    props.$smallBackgroundColor
      ? props.theme[props.$smallBackgroundColor] || props.$smallBackgroundColor
      : "transparent"};
`;

const MobileLayout = (props) => {
  const { children } = props;

  return (
    <StyledContainer {...props}>
      <section>{children}</section>
      <BottomBar {...props} />
    </StyledContainer>
  );
};

export default MobileLayout;

MobileLayout.propTypes = {
  children: PropTypes.node,
};
