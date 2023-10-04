import React from "react";

import { InlineSpacer } from "@agir/front/genericComponents/Spacer";
import Button from "./Button";

export default {
  component: Button,
  title: "Generic/Button",
  parameters: {
    layout: "padded",
  },
  argTypes: {
    color: {
      control: {
        type: "select",
        options: Button.colors,
      },
    },
    icon: {
      control: {
        type: "select",
        options: Button.icons,
      },
    },
  },
};

const Template = (args) =>
  Button.colors.map((color) => (
    <div key={color} style={{ margin: 0, padding: " 0 0 1rem", lineHeight: 0 }}>
      <pre style={{ fontSize: 12 }}>{color}</pre>
      <Button {...args} color={color} />
      <InlineSpacer size=".5rem" />
      <Button {...args} small color={color} />
      <InlineSpacer size=".5rem" />
      <Button {...args} small color={color} disabled />
      <InlineSpacer size=".5rem" />
      <Button {...args} color={color} disabled />
    </div>
  ));

export const Default = Template.bind({});
Default.args = {
  color: "white",
  icon: undefined,
  small: false,
  block: false,
  wrap: false,
  disabled: false,
  loading: false,
  children: "Click me!",
};

export const Link = Template.bind({});
Link.args = {
  ...Default.args,
  link: true,
  href: "#",
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  ...Default.args,
  icon: Button.icons[Math.floor(Math.random() * Button.icons.length)],
};

export const WithIconRight = Template.bind({});
WithIconRight.args = {
  ...WithIcon.args,
  rightIcon: true,
};

export const NotWrapping = Template.bind({});
NotWrapping.args = {
  ...Default.args,
  children: "This text is so looooooooooooooooong",
  style: { maxWidth: 200 },
  block: true,
};

export const Wrapping = Template.bind({});
Wrapping.args = {
  ...Default.args,
  children: "This text is so long, it should wrap",
  style: { maxWidth: 200 },
  block: true,
  wrap: true,
};

export const BlockButton = Template.bind({});
BlockButton.args = {
  ...Default.args,
  block: true,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  loading: true,
};
