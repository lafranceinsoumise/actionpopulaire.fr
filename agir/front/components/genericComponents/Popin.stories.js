import React from "react";

import Popin from "./Popin";

export default {
  component: Popin,
  title: "Generic/Popin",
};

export const Default = (props) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const handleOpen = React.useCallback(() => setIsOpen(true), []);
  const handleDismiss = React.useCallback(() => setIsOpen(false), []);

  return (
    <div
      style={{
        position: "fixed",
        right: 0,
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
      <Popin {...props} isOpen={isOpen} onDismiss={handleDismiss}>
        <p style={{ border: "1px dashed crimson" }}>I am the Popin content !</p>
      </Popin>
    </div>
  );
};
