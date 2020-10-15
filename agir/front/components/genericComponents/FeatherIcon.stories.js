import React from "react";
import FeatherIcon, {
  allIcons,
  IconList,
  IconListItem,
  RawFeatherIcon,
} from "./FeatherIcon";

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
    inline: {
      name: "Aligner sur le texte",
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
    inline: true,
  },
  fontSize: {
    name: "Taille de la police du texte",
  },
};
WithText.storyName = "Avec du texte";

export const AsList = () => (
  <>
    <p>Exemple de liste avec des icônes</p>
    <IconList>
      <IconListItem name="user">Avec du texte</IconListItem>
      <IconListItem name="activity">
        Avec du texte sur
        <br />
        plusieurs lignes
      </IconListItem>
      <IconListItem name="user">Avec du texte</IconListItem>
    </IconList>
  </>
);
AsList.args = {};
AsList.storyName = "En liste";
