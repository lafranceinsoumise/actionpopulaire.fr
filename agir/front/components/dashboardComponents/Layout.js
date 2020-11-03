import React from "react";
import PropTypes from "prop-types";
import {
  Column,
  Container,
  GrayBackground,
  Row,
} from "@agir/front/genericComponents/grid";
import Navigation from "@agir/front/dashboardComponents/Navigation";

const Layout = (props) => (
  <GrayBackground>
    <Container style={{ paddingTop: "64px" }}>
      <Row gutter={72}>
        <Column>
          <Navigation {...props} />
        </Column>
        <Column grow>{props.children}</Column>
      </Row>
    </Container>
  </GrayBackground>
);

export default Layout;

Layout.propTypes = {
  active: PropTypes.oneOf(["events", "groups", "notifications", "menu"]),
  routes: PropTypes.shape({
    events: PropTypes.string.isRequired,
    groups: PropTypes.string.isRequired,
    notifications: PropTypes.string.isRequired,
    menu: PropTypes.string.isRequired,
  }),
  children: PropTypes.node,
};
Layout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "#groupes",
    notifications: "#notifications",
  },
};
