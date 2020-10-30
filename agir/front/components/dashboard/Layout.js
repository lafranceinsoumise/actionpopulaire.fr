import React from "react";
import PropTypes from "prop-types";
import {
  Column,
  Container,
  GrayBackground,
  Row,
} from "@agir/front/genericComponents/grid";
import Navigation from "@agir/front/dashboard/Navigation";
import Card from "@agir/front/genericComponents/Card";

const Layout = (props) => (
  <GrayBackground>
    <Container>
      <Row gutter={72}>
        <Column>
          <Navigation {...props} />
        </Column>
        <Column grow>
          <Card />
          <Card />
        </Column>
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
};
