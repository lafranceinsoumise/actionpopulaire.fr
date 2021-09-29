import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Announcements from "@agir/front/dashboardComponents/Announcements";
import FacebookLoginAd from "@agir/front/dashboardComponents/FacebookLoginAd";
import Navigation, {
  SecondaryNavigation,
} from "@agir/front/dashboardComponents/Navigation";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import ActionButtons from "@agir/front/app/ActionButtons";
import { LayoutTitle, LayoutSubtitle } from "./StyledComponents";

const FixedColumn = styled(Column)`
  position: sticky;
  top: 4.5rem;
  padding-top: 4.5rem;
  z-index: ${(props) => props.theme.zindexMainContent};
`;

const SidebarColumn = styled(Column)`
  padding-top: 4.5rem;
`;

const MainColumn = styled(Column)`
  padding-top: 4.5rem;
`;

const MainContainer = styled(Container)`
  padding-bottom: 4.5rem;

  & > ${Row} {
    flex-wrap: nowrap;
  }
`;

const Layout = (props) => {
  const { title, subtitle, children } = props;
  return (
    <MainContainer {...props}>
      <Row gutter={50} align="flex-start">
        <FixedColumn width="320px">
          <Navigation {...props} />
        </FixedColumn>
        <MainColumn grow>
          <section>
            {props.title ? (
              <header>
                <LayoutTitle>{title}</LayoutTitle>
                <LayoutSubtitle>{subtitle}</LayoutSubtitle>
              </header>
            ) : null}
            {children}
          </section>
        </MainColumn>
        <SidebarColumn>
          <div style={{ marginBottom: "2rem" }}>
            <h4 style={{ margin: "0 0 .5rem" }}>Mes actions</h4>
            <ActionButtons />
          </div>
          <FacebookLoginAd />
          <Announcements />
          <SecondaryNavigation />
        </SidebarColumn>
      </Row>
    </MainContainer>
  );
};

export default Layout;

Layout.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  children: PropTypes.node,
};
