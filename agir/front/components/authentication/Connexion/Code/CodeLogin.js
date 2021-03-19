import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import { checkCode } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory } from "react-router-dom";
import useSWR from "swr";

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

const CodeConnexion = ({ localCode = "" }) => {
  const history = useHistory();
  const [code, setCode] = useState("");
  const [error, setError] = useState({});
  const [submitted, setSubmitted] = useState(false);

  let { data: session, mutate: mutate } = useSWR("/api/session/");
  console.log("SWR session", session);

  const handleCode = useCallback((e) => {
    setCode(e.target.value);
  }, []);

  const handleSubmit = async () => {
    setSubmitted(true);
    setError({});
    const data = await checkCode(code);
    setSubmitted(false);
    console.log("data : ", data);
    if (data.error) {
      setError(data.error);
      return;
    }

    mutate("/api/session/");
  };

  useEffect(() => {
    if (session.user === false) return;
    const route = routeConfig.events.getLink();
    history.push(route);
  }, [session]);

  return (
    <Container>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>Votre code de connexion vous a été envoyé par e-mail</h1>

      {localCode && (
        <h2
          style={{
            padding: "1rem 2rem",
            margin: "0",
            marginTop: "1rem",
            backgroundColor: style.green100,
          }}
        >
          {localCode}
        </h2>
      )}

      <p style={{ marginTop: "2rem" }}>
        Entrez le code de connexion que nous avons envoyé à{" "}
        <strong>danielle@simonnet.fr</strong>
      </p>
      <p style={{ marginBottom: "0" }}>
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
          <Button color="primary" onClick={handleSubmit} disabled={submitted}>
            Valider
          </Button>
        </div>
      </Form>
    </Container>
  );
};

CodeConnexion.propTypes = {
  localCode: PropTypes.string,
};

export default CodeConnexion;
