import React, { useState } from "react";
import OnlineUrlField from "./OnlineUrlField";

export default {
  component: OnlineUrlField,
  title: "EventForm/OnlineUrlField",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => {
  const [value, setValue] = useState(args.value);

  const handleChange = (name, value) => {
    setValue(value);
  };

  return <OnlineUrlField {...args} onChange={handleChange} value={value} />;
};

export const Default = Template.bind({});

Default.args = {
  name: "visioConf",
  label: "Visio-conférence",
  placeholder: "URL de la visio-conférence (facultatif)",
  error: "",
};

export const Error = Template.bind({});

Error.args = {
  ...Default.args,
  value: "https://video.net",
  error: "Entrez une URL valide",
};

export const WithoutDefault = Template.bind({});

WithoutDefault.args = {
  ...Default.args,
  defaultUrl: "",
};

export const Disabled = Template.bind({});

Disabled.args = {
  ...Default.args,
  disabled: true,
  value: "vimeo.com",
};
