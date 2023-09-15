import React from "react";

import SpendingRequestStatus, { STATUS_CONFIG } from "./SpendingRequestStatus";

const labels = Object.values(STATUS_CONFIG).reduce(
  (o, v) => ({
    ...o,
    [v.id]: v.label,
  }),
  {},
);

export default {
  component: SpendingRequestStatus,
  title: "Donations/SpendingRequest/SpendingRequestStatus",
  parameters: {
    layout: "padded",
  },
  argTypes: {
    code: {
      control: {
        options: Object.keys(labels),
        labels,
      },
    },
  },
};

const Template = (args) =>
  args.code ? (
    <SpendingRequestStatus {...args} />
  ) : (
    <div
      style={{
        display: "flex",
        flexFlow: "column nowrap",
        alignItems: "start",
        gap: args.small ? "0.5rem" : "1rem",
        maxWidth: 400,
      }}
    >
      {Object.keys(labels).map((code) => (
        <SpendingRequestStatus key={code} {...args} code={code} />
      ))}
    </div>
  );

export const Default = Template.bind({});
Default.args = {
  code: Object.keys(labels)[0],
  label: "",
  explanation:
    "Cette demande a déjà été validée par un⋅e animateur⋅rice ou gestionnaire du groupe. Pour permettre sa transmission, elle doit encore être validée par un deuxième animateur⋅rice ou gestionnaire.",
};

export const All = Template.bind({});
All.args = {
  code: "",
  label: "",
  explanation:
    "Cette demande a déjà été validée par un⋅e animateur⋅rice ou gestionnaire du groupe. Pour permettre sa transmission, elle doit encore être validée par un deuxième animateur⋅rice ou gestionnaire.",
};
