import React from "react";

import Popin from "./Popin";

export default {
  component: Popin,
  title: "Generic/Popin",
};

const Template = (args) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const handleOpen = React.useCallback(() => setIsOpen(true), []);
  const handleDismiss = React.useCallback(() => setIsOpen(false), []);

  return (
    <div
      style={{
        position: "fixed",
        left: "50%",
        top: "50%",
        transform: "translate(-50%, -50%)",
        width: 50,
        height: 50,
        cursor: "pointer",
        background:
          "radial-gradient(crimson, transparent, crimson, transparent, crimson, transparent, crimson, transparent, crimson, transparent, crimson)",
        backgroundSize: "50% 50%",
      }}
      onMouseOver={handleOpen}
      onMouseLeave={handleDismiss}
    >
      <Popin {...args} isOpen={isOpen} onDismiss={handleDismiss}>
        <pre style={{ margin: 0, border: "1px dashed crimson" }}>
          I am the Popin content !
        </pre>
      </Popin>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  position: "bottom",
  shouldDismissOnClick: true,
};

const OpenTemplate = (args) => {
  return (
    <div
      style={{
        position: "fixed",
        left: "50%",
        top: "50%",
        transform: "translate(-50%, -50%)",
        width: 50,
        height: 50,
        cursor: "pointer",
        background:
          "radial-gradient(teal, transparent, teal, transparent, teal, transparent, teal, transparent, teal, transparent, teal)",
        backgroundSize: "50% 50%",
      }}
    >
      <Popin {...args} isOpen>
        <pre style={{ display: "block", margin: 0, border: "1px dashed teal" }}>
          I am the Popin content !
        </pre>
      </Popin>
    </div>
  );
};

export const Open = OpenTemplate.bind({});
Open.args = {
  position: "bottom-right",
  shouldDismissOnClick: true,
};

export const OpenRight = OpenTemplate.bind({});
OpenRight.args = {
  position: "right",
  shouldDismissOnClick: true,
};

export const WithCloseButton = OpenTemplate.bind({});
WithCloseButton.args = {
  ...Open.args,
  hasCloseButton: true,
};
