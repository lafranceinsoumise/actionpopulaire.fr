import React from "react";

import LegacyButton, { buttonColors } from "./LegacyButton";
import { allIcons } from "./FeatherIcon";
import { Column, Row } from "@agir/front/genericComponents/grid";

export default {
  component: LegacyButton,
  title: "Generic/LegacyButton (deprecated)",
  argTypes: {
    color: {
      control: {
        type: "select",
        options: Object.keys(buttonColors),
      },
    },
    icon: {
      name: "Nom de l'icône",
      control: {
        type: "select",
        options: allIcons,
      },
    },
    small: {
      name: "Petit",
      control: "boolean",
    },
  },
};

const Template = (args) => <LegacyButton {...args} />;

export const Default = Template.bind({});
Default.args = {
  small: false,
  disabled: false,
  children: "Texte du bouton",
  $hasTransition: false,
};

export const PrimaryColor = Template.bind({});
PrimaryColor.args = {
  ...Default.args,
  color: "primary",
};

export const SecondaryColor = Template.bind({});
SecondaryColor.args = {
  ...Default.args,
  color: "secondary",
};

export const ConfirmedColor = Template.bind({});
ConfirmedColor.args = {
  ...Default.args,
  color: "confirmed",
};

export const DangerColor = Template.bind({});
DangerColor.args = {
  ...Default.args,
  color: "danger",
};

export const Unavailable = Template.bind({});
Unavailable.args = { ...Default.args, color: "unavailable" };

export const SmallExample = Template.bind({});
SmallExample.args = { ...Default.args, small: true };

export const DisabledExample = Template.bind({});
DisabledExample.args = { ...Default.args, disabled: true };

export const LinkLegacyButton = Template.bind({});
LinkLegacyButton.args = {
  ...Default.args,
  as: "a",
  href: "#some.link",
};

export const IconLegacyButton = Template.bind({});
IconLegacyButton.args = {
  ...Default.args,
  icon: "copy",
};

export const LegacyButtonAndLink = (args) => (
  <Row gutter={6} style={{ margin: "2rem" }}>
    <Column>
      <LegacyButton {...args}>Bouton</LegacyButton>
    </Column>
    <Column>
      <LegacyButton link href="#some.link" {...args}>
        Lien
      </LegacyButton>
    </Column>
  </Row>
);
LegacyButtonAndLink.args = {
  ...Default.args,
};

export const WithTransition = (args) => {
  const [state, setState] = React.useState(0);
  const colors = React.useMemo(() => Object.keys(buttonColors), []);
  const updateState = React.useCallback(() => {
    setState((state) => state + 1);
  }, []);
  const color = React.useMemo(
    () => colors[state % colors.length],
    [state, colors],
  );
  const small = React.useMemo(
    () => Boolean(Math.floor(state / colors.length) % 2),
    [state, colors],
  );

  return (
    <LegacyButton {...args} color={color} small={small} onClick={updateState} />
  );
};
WithTransition.args = {
  ...Default.args,
  $hasTransition: true,
};
