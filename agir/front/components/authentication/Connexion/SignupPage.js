import Helmet from "react-helmet";
import React from "react";
import logoMobile from "@agir/front/genericComponents/logos/action-populaire_mini.svg";
import { Hide } from "@agir/front/genericComponents/grid";
import Signup from "./Signup";
import LeftBlockDesktop from "./LeftBlockDesktop";
import { MainBlock, Container, BackgroundMobile } from "./styledComponents";

const SignupPage = () => {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Helmet>
        <meta name="title" content="Inscription" />
        <meta name="description" content="Rejoignez Action Populaire" />
      </Helmet>
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

          <Signup />
        </Container>

        <Hide over>
          <BackgroundMobile />
        </Hide>
      </MainBlock>
    </div>
  );
};

export default SignupPage;
