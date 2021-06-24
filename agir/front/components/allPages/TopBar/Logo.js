import React from "react";

import LogoAP from "@agir/front/genericComponents/LogoAP";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

const Logo = () => {
  const small = useResponsiveMemo(true, false);
  return (
    <LogoAP
      small={small}
      style={{ height: small ? "2.188rem" : "3.5rem", width: "auto" }}
    />
  );
};

export default Logo;
