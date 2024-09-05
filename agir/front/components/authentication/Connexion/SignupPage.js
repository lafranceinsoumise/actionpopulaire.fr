import React from "react";

import { Hide } from "@agir/front/genericComponents/grid";
import { IconLogo } from "@agir/front/genericComponents/LogoAP";
import LeftBlockDesktop from "./LeftBlockDesktop";
import Signup from "./Signup";
import { BackgroundMobile, Container, MainBlock } from "./styledComponents";

const SignupPage = () => {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <LeftBlockDesktop />
      <MainBlock>
        <Container>
          <Hide $over style={{ textAlign: "center", marginTop: "3rem" }}>
            <IconLogo style={{ width: "69px", marginBottom: "1.5rem" }} />
          </Hide>
          <Signup />
        </Container>
        <Hide $over>
          <BackgroundMobile />
        </Hide>
      </MainBlock>
    </div>
  );
};

export default SignupPage;
