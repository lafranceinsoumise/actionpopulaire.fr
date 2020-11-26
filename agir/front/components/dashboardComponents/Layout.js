import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import {
  Column,
  Container,
  GrayBackground,
  Row,
} from "@agir/front/genericComponents/grid";
import Navigation from "@agir/front/dashboardComponents/Navigation";
import Footer from "@agir/front/dashboardComponents/Footer";

export const LayoutTitle = styled.h1`
  font-size: 28px;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    font-size: 20px;
    margin: 0 25px;
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
`;

const Layout = (props) => (
  <GrayBackground>
    <MainContainer>
      <Row gutter={72} align="flex-start">
        <FixedColumn>
          <Navigation {...props} />
        </FixedColumn>
        <MainColumn grow>
          <section>
            {props.title ? (
              <header>
                <LayoutTitle>{props.title}</LayoutTitle>
              </header>
            ) : null}
            {props.children}
          </section>
        </MainColumn>
      </Row>
    </MainContainer>
    <Footer />
  </GrayBackground>
);

export default Layout;

Layout.propTypes = {
  active: PropTypes.oneOf([
    "events",
    "groups",
    "activity",
    "required-activity",
    "menu",
  ]),
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
  children: PropTypes.node,
};
Layout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "/mes-groupes",
    activity: "/activite",
  },
};
