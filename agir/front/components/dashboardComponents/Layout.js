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

const PageColumn = styled(Column)`
  min-height: 100vh;
`;

const PageTitle = styled.h1`
  font-size: 28px;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    margin: 0 25px;
    font-size: 20px;
  }
`;

const Layout = (props) => (
  <GrayBackground>
    <Container gutter={72} style={{ paddingTop: "64px" }}>
      <Row gutter={72}>
        <Column>
          <Navigation {...props} />
        </Column>
        <PageColumn grow>
          {props.title ? (
            <header>
              <PageTitle>{props.title}</PageTitle>
            </header>
          ) : null}
          {props.children}
        </PageColumn>
      </Row>
    </Container>
  </GrayBackground>
);

export default Layout;

Layout.propTypes = {
  active: PropTypes.oneOf(["events", "groups", "activity", "menu"]),
  routes: PropTypes.shape({
    events: PropTypes.string.isRequired,
    groups: PropTypes.string.isRequired,
    activity: PropTypes.string.isRequired,
    menu: PropTypes.string.isRequired,
  }),
  title: PropTypes.string,
  children: PropTypes.node,
};
Layout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "#groupes",
    activity: "/activite",
  },
};
