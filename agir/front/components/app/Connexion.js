import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";

import logoDesktop from "../genericComponents/logos/action-populaire.svg";
import logoMobile from "../genericComponents/logos/action-populaire_mini.svg";
import bgDesktop from "../genericComponents/images/login_bg_desktop.svg";
import bgMobile from "../genericComponents/images/login_bg_mobile.svg";
import facebookImg from "../genericComponents/images/facebook_circle.svg";
import arrowRight from "../genericComponents/images/arrow-right.svg";
import chevronDown from "../genericComponents/images/chevron-down.svg";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

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

  .button-facebook {
    max-width: 100%;
    width: 400px;
    justify-content: center;
    font-weight: normal;
    background-color: white;
    border: 1px solid #C4C4C4;
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

// const FacebookButton = styled.Button`
//   &:hover{
//     background-color: #eee;
//   }
// `;

const InlineBlock = styled.span`
  display: inline-block;
  text-align: left;
`;

//const mockMails = ["mgoaziou@gmail.com", "test@franceinsoumise.org"];
const mockMails = ["mgoaziou@gmail.com"];

const Login = () => {
  return (
    <>
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
        placeholder="Adresse e-mail"
        onChange={() => {}}
        value=""
      />
    </div>
    <Button
      color="primary"
      style={{
        marginTop: "0.5rem",
        maxWidth: "100%",
        width: "400px",
        justifyContent: "center",
      }}
    >
      Me connecter
    </Button>
    </>
  )
};

const FacebookLogin = () => {
  return (
    <Button className="button-facebook">
      <img src={facebookImg} style={{ width: "24px", height: "24px" }} />
      &nbsp; Connexion avec Facebook
    </Button>
  );
};

const ToastNotConnected = () => {
  return (
  <div style={{ padding: "16px", border: "1px solid #000A2C", position: "relative", marginTop: "32px" }}>
    <div style={{position: "absolute", left: "0", top: "0", height: "100%", width: "6px", backgroundColor: "#E93A55"}}></div>
    Vous devez vous connecter pour accéder à cette page
  </div>);
};

const Connexion = () => {

  const [existantMails, setExistantMails] = useState(mockMails);
  const [showMore, setShowMore] = useState(false);

  const handleShowMore = () => {
    setShowMore(true);
  };

  return (
    <>
      <div style={{ display: "flex" }}>
        <LeftBlock>
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
          <div style={{width:"100%", height:"450px"}}></div>

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

          <InlineBlock style={{ width: "400px", maxWidth: "100%", paddingLeft: "32px", paddingRight: "32px" }}>
            <div className="mobile-only" style={{ textAlign: "center", marginTop: "69px" }}>
              <img src={logoMobile} style={{ width: "69px", marginBottom: "24px" }} alt="" />
            </div>
            <h1>Je me connecte</h1>

            <InlineBlock style={{ marginTop: "8px" }}>
              <span>Pas encore de compte ?</span>
              &nbsp;
              <span style={{ color: style.primary500, fontWeight: 700 }}>
                Je m'inscris
              </span>
            </InlineBlock>

            <ToastNotConnected />

            {/* EXISTANT MAILS */}
            {(existantMails.length > 0) &&
            <div style={{marginTop: "24px"}}>
              <span style={{fontWeight:500}}>À mon compte :</span>
                
              {existantMails.map((mail, id) => (
              <Button
                key={id}
                color="primary"
                style={{
                  marginTop: "0.5rem",
                  marginLeft: "0px",
                  maxWidth: "100%",
                  width: "400px",
                  justifyContent: "space-between",
                }}
              >
                {mail}
                <img src={arrowRight} style={{color:"white"}} alt=""/>
              </Button>
              ))}
            </div>}

            {!showMore && <InlineBlock onClick={handleShowMore}
                style={{fontWeight: "700", color: style.primary500, marginTop: "21px", cursor: "pointer" }}>
                Afficher tout <img src={chevronDown} alt=""/>
            </InlineBlock>}

            {showMore && 
            <div style={{ textAlign: "center", margin: "6px", fontSize: "14px" }} >
              OU
            </div>}

            {(showMore || !(existantMails.length > 0)) && <>
            <Login />
            <div style={{ textAlign: "center", margin: "21px", fontSize: "14px" }} >OU</div>
            <FacebookLogin />
            </>}

            {showMore && <div className="mobile-center" style={{marginTop: "24px"}}>
              Pas encore de compte ? <br/>
              <InlineBlock style={{fontWeight: "700", color: style.primary500}}>
                  Rejoignez Action Populaire
              </InlineBlock>
            </div>}

          </InlineBlock>

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
