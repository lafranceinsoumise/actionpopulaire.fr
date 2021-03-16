import React, { useState, useCallback } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import mailChecked from "@agir/front/genericComponents/images/mail-checked.svg";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import JLM_rounded from "@agir/front/genericComponents/images/JLM_rounded.png";
import LFI_rounded from "@agir/front/genericComponents/images/LFI_rounded.png";
import checkCirclePrimary from "@agir/front/genericComponents/images/check-circle-primary.svg";

const Container = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 24px;

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
  margin-top: 2rem;
  display: flex;
  text-align: left;

  Button {
    margin-top: 1.5rem;
    margin-left: 0.625rem;
    width: 140px;
    height: 41px;
    justify-content: center;
  }

  & > :first-child {
    width: 100%;
  }

  @media (max-width: ${style.collapse}px) {
    flex-flow: wrap;
    div {
      width: 100%;
      Button {
        width: 100%;
        margin-left: 0;
        margin-top: 0.875rem;
      }
    }
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const ContainerRadio = styled.div`
  display: flex;
  max-width: 525px;
  width: 100%;
  @media (max-width: ${style.collapse}px) {
    flex-direction: column;
  }
`;

const RadioBlock = styled.div`
  width: 250px;
  display: flex;
  flex-align: center;
  text-align: center;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 24px;
  margin-top: 38px;
  position: relative;
  cursor: pointer;
  transition: ease 0.2s;

  @media (max-width: ${style.collapse}px) {
    flex-direction: row;
    width: 100%;
  }
  &.responsive-margin {
    @media (max-width: ${style.collapse}px) {
      margin-top: 16px;
    }
    @media (min-width: ${style.collapse}px) {
      margin-left: 24px;
    }
  }

  ${(props) => {
    if (props.$checked) {
      return `
        border 2px solid ${style.primary500};
        box-shadow: 0px 0px 3px #571AFF, 0px 2px 0px rgba(87, 26, 255, 0.2);
        `;
    } else {
      return `
        border: 1px solid #C4C4C4;
      `;
    }
  }};

  &:hover {
    border-color: ${style.primary500};
  }

  > div {
    position: absolute;
    right: 12px;
    top: 12px;
    margin: 0px;
  }
  input {
    position: absolute;
    right: 12px;
    top: 12px;
    margin: 0px;
    border: 1px solid #333;
  }
  span {
    ${(props) => props.$checked && `color: ${style.primary500}`};
    margin-top: 14px;
    padding: 10px;
    font-weight: 600;
    font-size: 16px;
  }
  img {
    width: 114px;
  }
`;

const InputRadio = styled.div`
  div {
    width: 16px;
    height: 16px;
    border: 1px solid #000a2c;
    border-radius: 20px;
  }
  img {
    width: 16px;
  }
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
        <p style={{ marginBottom: "0" }}>
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
        <p style={{ marginBottom: "0" }}>
          Si vous aviez déjà un compte, vous pouvez vous connecter avec un autre
          e-mail
        </p>
      </>
    ),
  },
  {
    img: (
      <div style={{ display: "inline-flex", fontWeight: 600 }}>
        {" "}
        <FeatherIcon
          name="check"
          color="green"
          strokeWidth={4}
          width="1rem"
        />{" "}
        &nbsp;Votre compte a été créé
      </div>
    ),
    title: "Pour quelle campagne rejoignez-vous Action Populaire ?",
    description: "Nous vous suggérerons des actions qui vous intéressent",
  },
];

const CodeSignin = () => {
  const [code, setCode] = useState("");
  const [reasonChecked, setReasonChecked] = useState(0);
  const [step, setStep] = useState(0);

  const handleCode = (e) => {
    setCode(e.target.value);
  };

  const handleReasonChecked = (value) => {
    setReasonChecked(value);
  };

  const handleCodeValidation = useCallback(() => {
    setStep((index) => {
      if (index < 2) return index + 1;
      else return 0;
    });
  });

  return (
    <Container>
      {stepItems[step].img}
      <h1>{stepItems[step].title}</h1>
      <div style={{ marginTop: "2rem" }}>{stepItems[step].description}</div>

      {2 === step && (
        <ContainerRadio>
          <RadioBlock
            onClick={() => handleReasonChecked(0)}
            $checked={0 === reasonChecked}
          >
            <img src={JLM_rounded} alt="" />
            <span>La campagne présidentielle 2022</span>
            <InputRadio>
              {0 === reasonChecked ? (
                <img src={checkCirclePrimary} alt="" />
              ) : (
                <div></div>
              )}
            </InputRadio>
          </RadioBlock>
          <RadioBlock
            onClick={() => handleReasonChecked(1)}
            $checked={1 === reasonChecked}
            className="responsive-margin"
          >
            <img src={LFI_rounded} alt="" />
            <span>Une autre campagne de la France Insoumise</span>
            <InputRadio>
              {1 === reasonChecked ? (
                <img src={checkCirclePrimary} alt="" />
              ) : (
                <div></div>
              )}
            </InputRadio>
          </RadioBlock>
        </ContainerRadio>
      )}

      {0 === step && (
        <Form>
          <TextField
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
            marginTop: "2rem",
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
