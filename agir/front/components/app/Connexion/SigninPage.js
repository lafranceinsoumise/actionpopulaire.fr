import React from "react";
import logoMobile from "@agir/front/genericComponents/logos/action-populaire_mini.svg";
import bgMobile from "@agir/front/genericComponents/images/login_bg_mobile.svg";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { Hide } from "@agir/front/genericComponents/grid";
import SignIn from "./Signin";
import LeftBlockDesktop from "./LeftBlockDesktop";

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

const Container = styled.div`
  display: inline-block;
  text-align: left;
  width: 500px;
  max-width: 100%;

  @media (max-width: ${style.collapse}px) {
    padding-left: 2rem;
    padding-right: 2rem;
  }
`;

const BackgroundMobile = styled.div`
  width: 100%;
  height: 150px;
  background-image: url(${bgMobile});
  background-size: cover;
  background-repeat: no-repeat;
`;

const SigninPage = () => {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <LeftBlockDesktop />
      <MainBlock>
        <Container>
          <Hide over style={{ textAlign: "center", marginTop: "69px" }}>
            <img
              src={logoMobile}
              alt="logo"
              style={{ width: "69px", marginBottom: "1.5rem" }}
            />
          </Hide>

          <SignIn />
        </Container>

        <Hide over>
          <BackgroundMobile />
        </Hide>
      </MainBlock>
    </div>
  );
};

export default SigninPage;
