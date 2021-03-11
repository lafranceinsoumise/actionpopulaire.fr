import React from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";

import logoDesktop from "../genericComponents/logos/action-populaire.svg";
import logoMobile from "../genericComponents/logos/action-populaire_mini.svg";

import bgDesktop from "../genericComponents/images/login_bg_desktop.svg";
import bgMobile from "../genericComponents/images/login_bg_mobile.svg";
import facebookImg from "../genericComponents/images/facebook_circle.svg";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const LeftBlock = styled.div`
  width: 40%;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const MainBlock = styled.div`
  width: 60%;

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

    h1 {
      font-size: 28px;
    }

    .mobile-only {
      display: block;
    }
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const Connexion = () => {
  return (
    <>
      <div style={{ display: "flex" }}>
        <LeftBlock
          style={{
            height: "100vh",
            backgroundColor: style.secondary100,
            position: "relative",
          }}
        >
          <div style={{ padding: "37px" }}>
            <img src={logoDesktop} alt="" style={{ width: "200px" }} />

            <div style={{ textAlign: "center" }}>
              <InlineBlock
                style={{
                  maxWidth: "350px",
                  lineHeight: "21px",
                  textAlign: "left",
                }}
              >
                Le réseau social d’action pour la candidature de Jean-Luc
                Mélenchon <InlineBlock>pour 2022</InlineBlock>
              </InlineBlock>
            </div>
          </div>

          {/* <img src={bgDesktop} style={{width: "100%", marginTop: "100px"}} alt=""/> */}

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

        <MainBlock
          style={{
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
          }}
        >
          <div style={{ maxWidth: "400px" }}>
            <div className="mobile-only" style={{ textAlign: "center" }}>
              <img src={logoMobile} style={{ width: "69px" }} alt="" />
            </div>
            <h1>Je me connecte</h1>
            <InlineBlock style={{ marginTop: "8px" }}>
              <span>Pas encore de compte ?</span>
              &nbsp;
              <span style={{ color: style.primary500, fontWeight: 700 }}>
                Je m'inscris
              </span>
            </InlineBlock>
            <div
              style={{
                boxSizing: "border-box",
                margin: "0 auto",
                marginTop: "24px",
              }}
            >
              <TextField
                error=""
                id="field"
                label="Adresse e-mail"
                onChange={() => {}}
                value=""
              />
            </div>
            <Button
              color="primary"
              style={{
                marginTop: "0.5rem",
                maxWidth: "100%",
                width: "330px",
                justifyContent: "center",
              }}
            >
              Me connecter
            </Button>
            <div
              style={{ textAlign: "center", margin: "21px", fontSize: "14px" }}
            >
              OU
            </div>
            <Button
              style={{
                maxWidth: "100%",
                width: "330px",
                justifyContent: "center",
                fontWeight: "normal",
                backgroundColor: "white",
                border: "1px solid #C4C4C4",
              }}
            >
              <img
                src={facebookImg}
                style={{ width: "24px", height: "24px" }}
                alt=""
              />
              &nbsp; Connexion avec Facebook
            </Button>
          </div>

          <div
            className="mobile-only"
            style={{ width: "100%", height: "150px" }}
          ></div>

          <div
            className="mobile-only"
            style={{
              position: "absolute",
              bottom: "0px",
              left: "0px",
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
