import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;

  h1 {
    font-size: 28px;
    font-weight: 700,
    line-height: 39px;
    text-align: center;
    margin-bottom: 0px;
    margin-top: 1rem;
  }
  p {
    text-align: center;
  }

  @media (max-width: ${style.collapse}px) {
    display: block;
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
    font-weight: 600;
    width: 100%;
  }

  @media (max-width: ${style.collapse}px) {
    flex-flow: wrap;
    & > :first-child {
      width: 100%;
    }
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

const CodeConnexion = () => {
  const [code, setCode] = useState("");

  const handleCode = (e) => {
    setCode(e.target.value);
  };

  return (
    <Container>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>Plus qu’une étape pour rejoindre l’action !</h1>
      <p style={{ marginTop: "2rem" }}>
        Entrez le code de connexion que nous avons envoyé à{" "}
        <strong>danielle@simonnet.fr</strong>
      </p>
      <p style={{ marginBottom: "0px" }}>
        Si l’adresse e-mail n’est pas reconnue, il vous sera proposé de vous
        inscrire.
      </p>

      <Form>
        <TextField
          error=""
          label="Code de connexion"
          placeholder=""
          onChange={handleCode}
          value={code}
        />
        <div>
          <Button color="primary">Valider</Button>
        </div>
      </Form>
    </Container>
  );
};

export default CodeConnexion;
