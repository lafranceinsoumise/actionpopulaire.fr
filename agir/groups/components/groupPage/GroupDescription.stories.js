import React from "react";

import GroupDescription from "./GroupDescription";

export default {
  component: GroupDescription,
  title: "Group/GroupDescription",
};

const Template = (args) => {
  return <GroupDescription {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  description: `
  <p>
    Chocolate cake gummies fruitcake. Lemon drops chocolate bar jelly beans danish candy bonbon. Cotton candy dessert bonbon topping macaroon. <strong>Marzipan croissant apple pie powder halvah brownie bear claw.</strong> Carrot cake jelly-o tootsie roll cake jelly beans. Croissant gingerbread icing pudding ice cream candy canes. Candy canes wafer caramels gingerbread.
  </p>
  <p>
    Ice cream biscuit brownie gingerbread liquorice soufflé wafer soufflé. <a href="#">Fruitcake cake lollipop</a>. Gummies sesame snaps chocolate bar soufflé jelly-o candy marzipan sweet jujubes. Lemon drops cheesecake wafer chocolate bar dessert pie sesame snaps fruitcake. Brownie gummies marshmallow chocolate halvah macaroon.
  </p>
  `,
};
