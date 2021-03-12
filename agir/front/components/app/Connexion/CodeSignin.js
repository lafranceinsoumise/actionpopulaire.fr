import React, { useState, useCallback } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import mailChecked from "@agir/front/genericComponents/images/mail-checked.svg";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const Container = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;

  h1 {
    font-size: 28px;
    font-weight: 700,
    line-height: 39px;
    text-align: center;
    margin-bottom: 0px;
    margin-top: 16px;
    max-width: 450px;
  }
  p {
    text-align: center;
  }
`;

const Form = styled.div`
  box-sizing: border-box;
  margin: 0 auto;
  margin-top: 36px;
  display: flex;

  Button {
    margin-top: 24px;
    margin-left: 10px;
    width: 140px;
    height: 41px;
    justify-content: center;
  }

  //& > TextField {
  & > label {
    font-weight: 600;
    width: 100%;
  }

  @media (max-width: ${style.collapse}px) {
    flex-flow: wrap;
    //& > TextField {
    & > label {
      width: 100%;
    }
    div {
      width: 100%;
      Button {
        width: 100%;
        margin-left: 0px;
        margin-top: 14px;
      }
    }
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const stepItems = [
  {
    img: <RawFeatherIcon name="mail" width="41px" height="41px" />,
    title: (
      <>
        Plus qu’une étape pour <br />
        rejoindre l’action !
      </>
    ),
    description: (
      <>
        <p>
          Entrez le code de connexion que nous avons envoyé à{" "}
          <strong>danielle@simonnet.fr</strong>
        </p>
        <p style={{ marginBottom: "0px" }}>
          Si l’adresse e-mail n’est pas reconnue, il vous sera proposé de vous
          inscrire.
        </p>
      </>
    ),
  },
  {
    img: <img src={mailChecked} alt="" />,
    title: (
      <>
        Bienvenue sur&nbsp;<InlineBlock>Action Populaire !</InlineBlock>
      </>
    ),
    description: (
      <>
        <p>
          Vous allez créer un compte pour <strong>danielle@simonnet.fr</strong>
        </p>
        <p style={{ marginBottom: "0px" }}>
          Si vous aviez déjà un compte, vous pouvez vous connecter avec un autre
          e-mail
        </p>
      </>
    ),
  },
  {
    img: "",
    title: "Pour quelle campagne rejoignez-vous Action Populaire ?",
    description: "Nous vous suggérerons des actions qui vous intéressent",
  },
];

const CodeSignin = () => {
  const [code, setCode] = useState("");
  const [step, setStep] = useState(0);

  const handleCode = (e) => {
    setCode(e.target.value);
  };

  const handleCodeValidation = useCallback(() => {
    setStep((index) => index + 1);
  });

  return (
    <Container>
      {stepItems[step].img}

      <h1>{stepItems[step].title}</h1>

      <div style={{ marginTop: "32px" }}>{stepItems[step].description}</div>

      {0 === step && (
        <Form>
          <TextField
            error=""
            label="Code de connexion"
            placeholder=""
            onChange={handleCode}
            value={code}
          />
          <div>
            <Button color="primary" onClick={handleCodeValidation}>
              Valider
            </Button>
          </div>
        </Form>
      )}

      {0 < step && (
        <Button
          color="primary"
          onClick={handleCodeValidation}
          style={{
            width: "356px",
            maxWidth: "100%",
            marginTop: "36px",
            justifyContent: "center",
          }}
        >
          Continuer
        </Button>
      )}
    </Container>
  );
};

export default CodeSignin;
