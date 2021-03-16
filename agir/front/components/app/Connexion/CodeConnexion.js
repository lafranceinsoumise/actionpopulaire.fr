import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
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

const CodeConnexion = () => {
  const [code, setCode] = useState("");

  const handleCode = (e) => {
    setCode(e.target.value);
  };

  return (
    <Container>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>Plus qu’une étape pour rejoindre l’action !</h1>
      <p style={{ marginTop: "32px" }}>
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
