import React from "react";
import Card from "./Card";
import { Column, Container, GrayBackgrund, Row } from "./grid";

export default {
  title: "Generic/Grid",
};

const lorem =
  "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod " +
  "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim " +
  "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea " +
  "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate " +
  "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat " +
  "cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";

const Template = () => (
  <GrayBackgrund>
    <Container>
      <Row>
        <Column fill>
          <Card>{lorem}</Card>
          <Card>{lorem}</Card>
          <Card>{lorem}</Card>
        </Column>
        <Column width="434px">
          <Card>{lorem}</Card>
          <Card>{lorem}</Card>
          <Card>{lorem}</Card>
        </Column>
      </Row>
    </Container>
  </GrayBackgrund>
);

export const FixedSideBarExample = Template.bind({});
FixedSideBarExample.args = {};
