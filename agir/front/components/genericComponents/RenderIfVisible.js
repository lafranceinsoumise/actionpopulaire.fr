import React from "react";
import TrackVisibility from "react-on-screen";

const RenderIfVisibile = ({ children, ...rest }) => (
  <TrackVisibility once offset={250} {...rest}>
    {({ isVisible }) => isVisible && children}
  </TrackVisibility>
);

export default RenderIfVisibile;
