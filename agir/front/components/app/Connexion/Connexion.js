import React from "react";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import logoMobile from "@agir/front/genericComponents/logos/action-populaire_mini.svg";
import bgDesktop from "@agir/front/genericComponents/images/login_bg_desktop.svg";
import bgMobile from "@agir/front/genericComponents/images/login_bg_mobile.svg";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import { Hide } from "@agir/front/genericComponents/grid";

import Login from "./Login";
import SignIn from "./Signin";

const LeftBlock = styled.div`
  width: 40%;
  background-color: ${style.secondary100};
  position: relative;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const MainBlock = styled.div`
  width: 60%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  h1 {
    margin: 0px;
    font-weight: 700;
    font-size: 40px;
  }

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    display: block;
    text-align: center;

    h1 {
      font-size: 28px;
    }

    .mobile-center {
      text-align: center;
    }
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const Container = styled.div`
  display: inline-block;
  text-align: left;
  //width: 500px; // For Signin
  width: 400px;
  max-width: 100%;

  @media (max-width: ${style.collapse}px) {
    padding-left: 32px;
    padding-right: 32px;
  }
`;

const BackgroundDesktop = styled.div`
  position: absolute;
  bottom: 0px;
  left: 0px;
  width: 100%;
  height: 450px;
  background-image: url(${bgDesktop});
  background-size: cover;
  background-repeat: no-repeat;
`;

const BackgroundMobile = styled.div`
  width: 100%;
  height: 150px;
  background-image: url(${bgMobile});
  background-size: cover;
  background-repeat: no-repeat;
`;

const Title = styled.div`
  text-align: center;
  div {
    display: inline-block;
    text-align: left;
    line-height: 21px;
    max-width: 350px;
  }
`;

const Connexion = () => {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <LeftBlock>
        <div style={{ padding: "37px", paddingBottom: "450px" }}>
          <LogoAP style={{ width: "200px" }} />
          <Title>
            <div>
              Le réseau social d’action pour la candidature de Jean-Luc
              Mélenchon <InlineBlock>pour 2022</InlineBlock>
            </div>
          </Title>
        </div>
        <BackgroundDesktop />
      </LeftBlock>

      <MainBlock>
        <Container>
          <Hide over style={{ textAlign: "center", marginTop: "69px" }}>
            <img
              src={logoMobile}
              alt="logo"
              style={{ width: "69px", marginBottom: "24px" }}
            />
          </Hide>

          {/* <Login /> */}
          <SignIn />
        </Container>

        <Hide over>
          <BackgroundMobile />
        </Hide>
      </MainBlock>
    </div>
  );
};

export default Connexion;
