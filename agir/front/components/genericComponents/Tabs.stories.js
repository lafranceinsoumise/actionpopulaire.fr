import React from "react";

import Tabs from "./Tabs";

export default {
  component: Tabs,
  title: "Generic/Tabs",
};

const tabs = [
  { id: "A", label: "Tab A" },
  { id: "B", label: "Tab B" },
  { id: "C", label: "Tab C" },
  { id: "D", label: "Tab D" },
  { id: "E", label: "Tab E" },
  { id: "F", label: "Tab F" },
  { id: "G", label: "Tab G" },
  { id: "H", label: "Tab H" },
  { id: "I", label: "Tab I" },
  { id: "J", label: "Tab J" },
  { id: "K", label: "Tab K" },
];

const paragraphs = [
  "Chocolate cake gummies fruitcake.",
  "Lemon drops chocolate bar jelly beans danish candy bonbon.",
  "Cotton candy dessert bonbon topping macaroon.",
  "Marzipan croissant apple pie powder halvah brownie bear claw.",
  "Carrot cake jelly-o tootsie roll cake jelly beans.",
  "Croissant gingerbread icing pudding ice cream candy canes.",
  "Candy canes wafer caramels gingerbread.",
  "Ice cream biscuit brownie gingerbread liquorice soufflé wafer soufflé.",
  "Fruitcake cake lollipop.",
  "Gummies sesame snaps chocolate bar soufflé jelly-o candy marzipan sweet jujubes.",
  "Lemon drops cheesecake wafer chocolate bar dessert pie sesame snaps fruitcake.",
  "Brownie gummies marshmallow chocolate halvah macaroon.",
  "Ice cream pudding sweet roll jelly beans apple pie liquorice tiramisu tiramisu sweet roll.",
  "Dragée wafer toffee.",
  "Cookie pastry cake sweet roll chocolate dessert.",
  "Gingerbread jelly beans cookie pudding ice cream topping.",
  "Gingerbread caramels jelly powder croissant cake jelly beans croissant lemon drops.",
  "Cake cotton candy gummies candy powder jujubes.",
  "Cupcake cotton candy sweet.",
  "Liquorice carrot cake icing.",
  "Croissant oat cake sweet roll.",
  "Cookie icing cookie biscuit halvah muffin.",
  "Gummi bears pudding icing carrot cake marzipan halvah marzipan bear claw.",
  "Muffin toffee biscuit lemon drops jelly beans.",
  "Wafer powder chocolate fruitcake tiramisu cake gingerbread jelly-o dessert.",
];

const Template = (args) => {
  const ts = tabs.slice(0, Math.max(1, args.howManyTabs));

  return (
    <div style={{ paddingTop: 0 }}>
      <Tabs {...args} tabs={ts}>
        {tabs.map((tab) => (
          <div key={tab.id} id={tab.id} style={{ padding: "1rem" }}>
            {paragraphs
              .sort(() => Math.random() - Math.random())
              .slice(0, 10)
              .map((paragraph, i) =>
                i === 0 ? (
                  <h3 key={paragraph}>{paragraph}</h3>
                ) : (
                  <span key={paragraph}>{paragraph} </span>
                ),
              )}
          </div>
        ))}
      </Tabs>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  activeIndex: 0,
  howManyTabs: 30,
};
