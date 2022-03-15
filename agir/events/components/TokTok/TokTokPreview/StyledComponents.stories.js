import React from "react";

import * as StyledComponents from "./StyledComponents";

export default {
  component: StyledComponents,
  title: "Events/TokTok/TokTokPreview/StyledComponents",
};

export const Banner = () => <StyledComponents.Banner />;

export const BackButton = () => <StyledComponents.BackButton />;

export const GroupCreationWarning = () => (
  <StyledComponents.GroupCreationWarning />
);
GroupCreationWarning.bind({});
GroupCreationWarning.parameters = {
  layout: "padded",
};
