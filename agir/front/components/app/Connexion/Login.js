import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import arrowRight from "@agir/front/genericComponents/images/arrow-right.svg";
import chevronDown from "@agir/front/genericComponents/images/chevron-down.svg";
import style from "@agir/front/genericComponents/_variables.scss";
import LoginMailEmpty from "./LoginMailEmpty";
import LoginFacebook from "./LoginFacebook";
import styled from "styled-components";

const Toast = styled.div`
  padding: 1rem;
  border: 1px solid #000a2c;
  position: relative;
  margin-top: 2rem;

  div {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 6px;
    background-color: #e93a55;
  }
`;

const ToastNotConnected = () => {
  return (
    <Toast>
      <div></div>
      Vous devez vous connecter pour accéder à cette page
    </Toast>
  );
};

//const mockMails = ["nom.prenom@email.com", "test@franceinsoumise.org"];
const mockMails = ["nom.prenom@email.com"];

const Login = () => {
  const [existantMails, setExistantMails] = useState(mockMails);
  const [showMore, setShowMore] = useState(false);

  const handleShowMore = () => {
    setShowMore(true);
  };

  return (
    <div style={{ width: "400px", maxWidth: "100%" }}>
      <h1>Je me connecte</h1>
      <div
        style={{
          marginTop: "0.5rem",
          display: "inline-block",
          textAlign: "left",
        }}
      >
        <span>Pas encore de compte ?</span>
        &nbsp;
        <span style={{ color: style.primary500, fontWeight: 700 }}>
          Je m'inscris
        </span>
      </div>

      {/* <ToastNotConnected /> */}

      {/* EXISTANT MAILS */}
      {existantMails.length > 0 && (
        <div style={{ marginTop: "24px" }}>
          <span style={{ fontWeight: 500 }}>À mon compte :</span>

          {existantMails.map((mail, id) => (
            <Button
              key={id}
              color="primary"
              style={{
                marginTop: "0.5rem",
                marginLeft: "0",
                maxWidth: "100%",
                width: "400px",
                justifyContent: "space-between",
              }}
            >
              {mail}
              <img src={arrowRight} style={{ color: "white" }} alt="" />
            </Button>
          ))}
        </div>
      )}

      {!showMore && (
        <div
          onClick={handleShowMore}
          style={{
            fontWeight: 700,
            color: style.primary500,
            marginTop: "21px",
            cursor: "pointer",
            display: "inline-block",
            textAlign: "left",
          }}
        >
          Afficher tout <img src={chevronDown} alt="" />
        </div>
      )}

      {showMore && (
        <div style={{ textAlign: "center", margin: "6px", fontSize: "14px" }}>
          OU
        </div>
      )}

      {(showMore || !(existantMails.length > 0)) && (
        <>
          <LoginMailEmpty />
          <div
            style={{ textAlign: "center", margin: "21px", fontSize: "14px" }}
          >
            OU
          </div>
          <LoginFacebook />
        </>
      )}

      {showMore && (
        <div className="mobile-center" style={{ marginTop: "24px" }}>
          Pas encore de compte ? <br />
          <div
            style={{
              fontWeight: "700",
              color: style.primary500,
              display: "inline-block",
              textAlign: "left",
            }}
          >
            Rejoignez Action Populaire
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
