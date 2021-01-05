import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Navigation, {
  SecondaryNavigation,
} from "@agir/front/dashboardComponents/Navigation";
import Announcements from "@agir/front/dashboardComponents/Announcements";
import Footer from "@agir/front/dashboardComponents/Footer";

export const LayoutSubtitle = styled.h2`
  color: ${style.black700};
  font-weight: 400;
  font-size: 14px;
  margin: 8px 0;

  @media (max-width: ${style.collapse}px) {
    padding: 0 1.5rem;
  }
`;

export const LayoutTitle = styled.h1`
  display: flex;
  align-items: center;
  font-size: 26px;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    font-size: 20px;
    padding: 0 1.5rem;
  }
`;

const FixedColumn = styled(Column)`
  position: relative;
  z-index: ${style.zindexMainContent};

  @media (min-width: ${style.collapse}px) {
    position: sticky;
    top: 72px;
    padding-top: 72px;
  }
`;

const Banner = styled.div`
  width: 100%;
  padding: 1rem 0 0;
  background-color: ${({ smallBackgroundColor }) =>
    smallBackgroundColor || "transparent"};

  &:empty {
    display: none;
  }

  @media (min-width: ${style.collapse}px) {
    display: none;
  }
`;

const SidebarColumn = styled(Column)`
  padding-top: 72px;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const MainColumn = styled(Column)`
  padding-top: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 0;
  }
`;

const MainContainer = styled(Container)`
  padding-bottom: 72px;
  @media (min-width: ${style.collapse}px) {
    & > ${Row} {
      flex-wrap: nowrap;
    }
  }
  @media (max-width: ${style.collapse}px) {
    padding-top: 24px;
    background-color: ${({ smallBackgroundColor }) =>
      smallBackgroundColor || "transparent"};
  }
`;

const Layout = (props) => (
  <>
    {props.hasBanner ? (
      <Banner {...props}>
        <Announcements displayType="banner" />
      </Banner>
    ) : null}
    <MainContainer {...props}>
      <Row gutter={50} align="flex-start">
        <FixedColumn width="320px">
          <Navigation {...props} />
        </FixedColumn>
        <MainColumn grow>
          <section>
            {props.title ? (
              <header>
                <LayoutTitle>{props.title}</LayoutTitle>
                <LayoutSubtitle>{props.subtitle}</LayoutSubtitle>
              </header>
            ) : null}
            {props.children}
          </section>
        </MainColumn>
        <SidebarColumn>
          <Announcements displayType="sidebar" />
          <SecondaryNavigation />
        </SidebarColumn>
      </Row>
    </MainContainer>
    <Footer desktopOnly={props.desktopOnlyFooter} />
  </>
);

export default Layout;

Layout.propTypes = {
  active: PropTypes.string,
  routes: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
          href: PropTypes.string,
        })
      ),
    ])
  ),
  title: PropTypes.string,
  subtitle: PropTypes.string,
  children: PropTypes.node,
  desktopOnlyFooter: PropTypes.bool,
  hasBanner: PropTypes.bool,
};
Layout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "/mes-groupes",
    activity: "/activite",
  },
  desktopOnlyFooter: true,
  hasBanner: false,
};
