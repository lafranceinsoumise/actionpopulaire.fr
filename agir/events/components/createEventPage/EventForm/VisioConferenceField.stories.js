import React, { useState } from "react";
import VisioConferenceField from "./VisioConferenceField";

export default {
  component: VisioConferenceField,
  title: "EventForm/VisioConference",
};

const Template = (args) => {
  const [value, setValue] = useState(args.value);

  const handleChange = (name, value) => {
    setValue(value);
  };

  return (
    <VisioConferenceField {...args} onChange={handleChange} value={value} />
  );
};

export const Default = Template.bind({});

Default.args = {
  name: "visioConf",
  label: "Visio-conférence",
  defaultUrl: "https://actionpopulaire.fr",
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
