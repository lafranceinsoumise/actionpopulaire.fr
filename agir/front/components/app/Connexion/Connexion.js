import React from "react";

import logoDesktop from "@agir/front/genericComponents/logos/action-populaire.svg";
import logoMobile from "@agir/front/genericComponents/logos/action-populaire_mini.svg";
import bgDesktop from "@agir/front/genericComponents/images/login_bg_desktop.svg";
import bgMobile from "@agir/front/genericComponents/images/login_bg_mobile.svg";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

// import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import Login from "./Login";
import SignIn from "./Signin";

const LeftBlock = styled.div`
  width: 40%;
  height: 100vh;
  background-color: ${style.secondary100};
  position: relative;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const MainBlock = styled.div`
  width: 60%;
  height: 100vh;
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

  .mobile-only {
    display: none;
  }

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    display: block;
    text-align: center;

    h1 {
      font-size: 28px;
    }

    .mobile-only {
      display: block;
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
  width: 500px;
  max-width: 100%;

  @media (max-width: ${style.collapse}px) {
    padding-left: 32px;
    padding-right: 32px;
  }
`;

const Connexion = () => {
  return (
    <>
      <div style={{ display: "flex" }}>
        <LeftBlock>
          <div style={{ padding: "37px" }}>
            <img src={logoDesktop} alt="" style={{ width: "200px" }} />

            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  display: "inline-block",
                  textAlign: "left",
                  maxWidth: "350px",
                  lineHeight: "21px",
                  textAlign: "left",
                }}
              >
                Le réseau social d’action pour la candidature de Jean-Luc
                Mélenchon <InlineBlock>pour 2022</InlineBlock>
              </div>
            </div>
          </div>

          {/* <img src={bgDesktop} style={{width: "100%", marginTop: "100px"}} alt=""/> */}
          <div style={{ width: "100%", height: "450px" }}></div>

          <div
            style={{
              position: "absolute",
              bottom: "0px",
              left: "0px",
              width: "100%",
              height: "450px",
              backgroundImage: `url(${bgDesktop})`,
              backgroundSize: "cover",
              backgroundRepeat: "no-repeat",
            }}
          ></div>
        </LeftBlock>

        <MainBlock>
          <Container>
            <div
              className="mobile-only"
              style={{ textAlign: "center", marginTop: "69px" }}
            >
              <img
                src={logoMobile}
                style={{ width: "69px", marginBottom: "24px" }}
                alt=""
              />
            </div>

            {/* <Login /> */}
            <SignIn />
          </Container>

          <div
            className="mobile-only"
            style={{
              width: "100%",
              height: "150px",
              backgroundImage: `url(${bgMobile})`,
              backgroundSize: "cover",
              backgroundRepeat: "no-repeat",
            }}
          ></div>
        </MainBlock>
      </div>
    </>
  );
};

export default Connexion;
