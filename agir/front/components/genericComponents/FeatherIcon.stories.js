import React from "react";
import FeatherIcon, { allIcons, RawFeatherIcon } from "./FeatherIcon";

export default {
  component: FeatherIcon,
  subcomponents: { RawFeatherIcon },
  title: "Generic/FeatherIcon",
  argTypes: {
    name: {
      name: "Nom de l'icône",
      control: {
        type: "select",
        options: allIcons,
      },
    },
    color: {
      name: "Couleur de l'icône",
      control: {
        type: "color",
      },
    },
    type: {
      name: "Type d'icône",
    },
  },
};

const Template = (args) => <FeatherIcon {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: "user",
};

export const Small = Template.bind({});
Small.args = {
  ...Default.args,
  type: "small",
};

export const WithText = ({ text, fontSize, ...args }) => (
  <div style={{ fontSize: `${fontSize}px` }}>
    <FeatherIcon {...args} /> <span>{text}</span>
  </div>
);
WithText.args = {
  ...Default.args,
  text: "Texte",
  fontSize: 16,
};

WithText.argTypes = {
  text: {
    type: "string",
    name: "Texte",
  },
  fontSize: {
    name: "Taille de la police du texte",
  },
};
WithText.storyName = "Avec du texte";
