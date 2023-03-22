import React from "react";

import LocationItems from "./LocationItems";

export default {
  component: LocationItems,
  title: "LocationField/LocationItems",
  argTypes: {
    onChange: { action: "onChange" },
  },
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => {
  return <LocationItems {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  name: "location",
  locations: [
    {
      id: "1",
      name: "Café du Croissant",
      address1: "142 rue de Montmartre",
      address2: "au fond à gauche",
      city: "Paris",
      zip: "75002",
      country: "FR",
    },
    {
      id: "2",
      name: "Café du Croissant",
      address1: "142 rue de Montmartre",
      address2: "au fond à gauche",
      city: "Paris",
      zip: "75002",
      country: "FR",
    },
    {
      id: "3",
      name: "Café du Croissant",
      address1: "142 rue de Montmartre",
      address2: "au fond à gauche",
      city: "Paris",
      zip: "75002",
      country: "FR",
    },
  ],
};
