import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Navigation from "@agir/front/dashboardComponents/Navigation";
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
  z-index: 2;

  @media (min-width: ${style.collapse}px) {
    position: sticky;
    top: 72px;
    padding-top: 72px;
  }
`;

const MainColumn = styled(Column)`
  padding-top: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 0;
  }
`;

const MainContainer = styled(Container)`
  min-height: calc(100vh - 72px);
  padding-bottom: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 24px;
    background-color: ${({ smallBackgroundColor }) =>
      smallBackgroundColor || "transparent"};
  }
`;

const Layout = (props) => (
  <>
    <MainContainer {...props}>
      <Row gutter={72} align="flex-start">
        <FixedColumn>
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
      </Row>
    </MainContainer>
    <Footer />
  </>
);

export default Layout;

Layout.propTypes = {
  active: PropTypes.oneOf(["events", "groups", "activity", "menu"]),
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
};
Layout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "/mes-groupes",
    activity: "/activite",
  },
};
