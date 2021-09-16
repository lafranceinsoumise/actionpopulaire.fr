import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";

import Navigation from "@agir/front/dashboardComponents/Navigation";

const StyledContainer = styled(Container)`
  padding-top: 24px;
  padding-bottom: 24px;
  background-color: ${({ smallBackgroundColor }) =>
    smallBackgroundColor || "transparent"};
`;

const MobileLayout = (props) => {
  const { children } = props;

  return (
    <StyledContainer {...props}>
      <Row gutter={50} align="flex-start">
        <Column style={{ paddingTop: 0 }} grow>
          <section>{children}</section>
        </Column>
      </Row>
      <Navigation {...props} />
    </StyledContainer>
  );
};

export default MobileLayout;

MobileLayout.propTypes = {
  children: PropTypes.node,
};
