import React from "react";

import Agenda from "./Agenda";
import { Container, GrayBackground } from "@agir/front/genericComponents/grid";

export default {
  component: Agenda,
  title: "Dashboard/Agenda",
};

const Template = (args) => (
  <GrayBackground>
    <Container>
      <Agenda {...args} />
    </Container>
  </GrayBackground>
);

export const Default = Template.bind({});
Default.args = {};
