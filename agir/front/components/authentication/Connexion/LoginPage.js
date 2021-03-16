import React from "react";
import logoMobile from "@agir/front/genericComponents/logos/action-populaire_mini.svg";
import { Hide } from "@agir/front/genericComponents/grid";
import Login from "./Login";
import LeftBlockDesktop from "./LeftBlockDesktop";
import { MainBlock, Container, BackgroundMobile } from "./styledComponents";

const LoginPage = () => {
  return (
    <div style={{ display: "flex" }}>
      <LeftBlockDesktop />
      <MainBlock>
        <Container>
          <Hide over style={{ textAlign: "center", marginTop: "3rem" }}>
            <img
              src={logoMobile}
              alt="logo"
              style={{ width: "69px", marginBottom: "1.5rem" }}
            />
          </Hide>

          <Login />
        </Container>

        <Hide over>
          <BackgroundMobile />
        </Hide>
      </MainBlock>
    </div>
  );
};

export default LoginPage;
