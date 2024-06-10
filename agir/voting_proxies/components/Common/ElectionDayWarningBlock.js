import React from "react";

import { WarningBlock } from "@agir/elections/Common/StyledComponents";

const ElectionDayWarningBlock = () => (
  <WarningBlock icon="alert-triangle" background="#ffe8d7" iconColor="#ff8c37">
    Pour que la procuration de vote puisse être validée et transmise au bureau
    de vote dans les temps,{" "}
    <strong>faites votre demande avant le jeudi 6 juin</strong>
     !
  </WarningBlock>
);

export default ElectionDayWarningBlock;
