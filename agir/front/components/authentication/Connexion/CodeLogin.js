import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { checkCode } from "@agir/front/authentication/api";

const Container = styled.div`
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;

  h1 {
    font-size: 26px;
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
    h1 {
      font-size: 18px;
    }
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
    max-width: 212px;
    width: 100%;
  }

  @media (max-width: ${style.collapse}px) {
    flex-flow: wrap;
    & > :first-child {
      max-width: 100%;
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
  const [error, setError] = useState({});

  const handleCode = (e) => {
    setCode(e.target.value);
  };

  const handleSubmit = async () => {
    setError({});
    const data = await checkCode(code);
    console.log("data : ", data);
    if (data.error) {
      setError(data.error);
      return;
    }
    // redirect to home
    // const route = routeConfig..getLink();
    // history.push(route);
  };

  return (
    <Container>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>Votre code de connexion vous a été envoyé par e-mail</h1>

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
          error={error && error.code}
          label="Code de connexion"
          onChange={handleCode}
          value={code}
        />
        <div>
          <Button color="primary" onClick={handleSubmit}>
            Valider
          </Button>
        </div>
      </Form>
    </Container>
  );
};

export default CodeConnexion;
