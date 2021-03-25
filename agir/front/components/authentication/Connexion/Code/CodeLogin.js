import React, { useState, useEffect, useCallback } from "react";
import { useHistory, useLocation } from "react-router-dom";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import TextField from "@agir/front/formComponents/TextField";

import { checkCode } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useBookmarkedEmails } from "@agir/front/authentication/hooks";
import {
  useSelector,
  useDispatch,
} from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import { setSessionContext } from "@agir/front/globalContext/actions";

const Container = styled.form`
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;

  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.5;
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

const LocalCode = styled.h2`
  padding: 1rem 2rem;
  margin: 0;
  margin-top: 1rem;
  background-color: ${style.green100};
`;

const CodeConnexion = () => {
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const history = useHistory();
  const location = useLocation();
  const [code, setCode] = useState("");
  const [error, setError] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [, bookmarkEmail] = useBookmarkedEmails();

  let { data: session, mutate: mutate } = useSWR("/api/session/");

  const handleCode = useCallback((e) => {
    setCode(e.target.value);
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setSubmitted(true);
      setError({});
      const data = await checkCode(code);
      setSubmitted(false);

      if (data.error) {
        setError(data.error);
        return;
      }

      mutate("/api/session/");
    },
    [code, mutate]
  );

  useEffect(() => {
    dispatch(setSessionContext(session));
  }, [dispatch, session]);

  useEffect(() => {
    if (!user) return;

    if (location.state) {
      location.state.email && bookmarkEmail(location.state.email);

      if (location.state.next) {
        history.push(location.state.next);
        return;
      }
    }

    const route = routeConfig.events.getLink();
    history.push(route);
  }, [user, bookmarkEmail, location, history]);

  return (
    <Container onSubmit={handleSubmit}>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>Votre code de connexion vous a été envoyé par e-mail</h1>

      {location.state && location.state.code && (
        <LocalCode>{location.state.code}</LocalCode>
      )}

      <p style={{ marginTop: "2rem" }}>
        Entrez le code de connexion que nous avons envoyé{" "}
        {location.state && location.state.email && (
          <>
            à <strong>{location.state.email}</strong>
          </>
        )}
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
          disabled={submitted}
        />
        <div>
          <Button color="primary" disabled={!code || submitted}>
            Valider
          </Button>
        </div>
      </Form>
    </Container>
  );
};

export default CodeConnexion;
