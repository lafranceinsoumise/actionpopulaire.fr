import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";

import Footer from "@agir/front/dashboardComponents/Footer";
import Navigation from "@agir/front/dashboardComponents/Navigation";

const StyledContainer = styled(Container)`
  padding-top: 24px;
  padding-bottom: 24px;
  background-color: ${({ smallBackgroundColor }) =>
    smallBackgroundColor || "transparent"};
`;

const MobileLayout = (props) => {
  const { children, desktopOnlyFooter, displayFooterOnMobileApp } = props;

  return (
    <>
      <StyledContainer {...props}>
        <Row gutter={50} align="flex-start">
          <Column style={{ paddingTop: 0 }} grow>
            <section>{children}</section>
          </Column>
        </Row>
        <Navigation {...props} />
      </StyledContainer>
      <Footer
        desktopOnly={desktopOnlyFooter}
        displayOnMobileApp={displayFooterOnMobileApp}
      />
    </>
  );
};

export default MobileLayout;

MobileLayout.propTypes = {
  children: PropTypes.node,
  desktopOnlyFooter: PropTypes.bool,
  displayFooterOnMobileApp: PropTypes.bool,
};
