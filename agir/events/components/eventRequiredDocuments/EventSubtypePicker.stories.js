import React from "react";

import EventSubtypePicker from "./EventSubtypePicker";

import subtypes from "@agir/front/mockData/eventSubtypes";

export default {
  component: EventSubtypePicker,
  title: "Event Required Documents/EventSubtypePicker",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);

  return (
    <div style={{ width: "100%", maxWidth: 372 }}>
      <EventSubtypePicker {...args} value={value} onChange={setValue} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  value: subtypes[0],
  options: subtypes,
  disabled: false,
};
