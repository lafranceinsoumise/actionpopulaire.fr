import React from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";

// import logo from "../genericComponents/images/logoActionPopulaire.png";
import logo from "../genericComponents/logos/action-populaire_small.svg";
import bgDesktop from "../genericComponents/images/login_bg_desktop.svg";
import facebookImg from "../genericComponents/images/facebook_circle.png";

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
  @media (max-width: ${style.collapse}px) {
    width: 100%;
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
            <img src={logo} alt="" style={{ maxWidth: "400px" }} />
          </div>
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
          }}
        >
          <div style={{ maxWidth: "400px" }}>
            <h1 style={{ margin: "0px", fontWeight: 700, fontSize: "48px" }}>
              Connexion
            </h1>
            <span style={{ marginTop: "8px" }}>Pas encore de compte ?</span>
            &nbsp;
            <span style={{ color: style.primary500, fontWeight: 500 }}>
              Je m'inscris
            </span>
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
        </MainBlock>
      </div>
    </>
  );
};

export default Connexion;
