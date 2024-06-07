import React from "react";

import { WarningBlock } from "@agir/elections/Common/StyledComponents";

const ElectionDayWarningBlock = () => (
  <WarningBlock icon="alert-triangle" background="#ffe8d7" iconColor="#ff8c37">
    Il n'est désormais plus possible de faire une demande de procuration pour
    les 8 et 9 juin !
  </WarningBlock>
);

export default ElectionDayWarningBlock;
