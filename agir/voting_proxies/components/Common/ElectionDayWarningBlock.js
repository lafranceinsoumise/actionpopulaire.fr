import React from "react";

import { WarningBlock } from "@agir/elections/Common/StyledComponents";

const ElectionDayWarningBlock = () => (
  <WarningBlock icon="alert-triangle" background="#ffe8d7" iconColor="#ff8c37">
    Pour que la procuration de vote puisse être validée et transmise au bureau
    de vote dans les temps,{" "}
    <strong>faites votre demande avant les jeudis 27 juin et 4 juillet</strong>
     !
  </WarningBlock>
);

export default ElectionDayWarningBlock;
