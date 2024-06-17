import React from "react";

import { WarningBlock } from "@agir/elections/Common/StyledComponents";

const ElectionDayWarningBlock = () => (
  <WarningBlock icon="alert-triangle" background="#ffe8d7" iconColor="#ff8c37">
    Pour que la procuration de vote puisse être validée et transmise au bureau
    de vote dans les temps,{" "}
    <strong>
      faites votre demande avant le 27 juin pour le premier tour et le 4 juillet
      pour le second
    </strong>
     !
  </WarningBlock>
);

export default ElectionDayWarningBlock;
