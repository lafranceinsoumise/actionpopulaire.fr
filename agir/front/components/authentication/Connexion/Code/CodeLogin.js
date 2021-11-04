import React, { useState, useMemo, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import TextField from "@agir/front/formComponents/TextField";

import { checkCode } from "@agir/front/authentication/api";
import { routeConfig, getRouteByPathname } from "@agir/front/app/routes.config";
import { useBookmarkedEmails } from "@agir/front/authentication/hooks";
import {
  useSelector,
  useDispatch,
} from "@agir/front/globalContext/GlobalContext";
import { getUser, getAuthentication } from "@agir/front/globalContext/reducers";
import { setSessionContext } from "@agir/front/globalContext/actions";
import { AUTHENTICATION } from "@agir/front/authentication/common";

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
  text-align: left;
  display: grid;
  grid-template-columns: 212px 140px;
  grid-gap: 0.625rem;
  width: 100%;
  max-width: 600px;
  justify-content: center;
  align-items: end;

  @media (max-width: ${style.collapse}px) {
    grid-template-columns: 100%;
  }

  & > ${Button} {
    margin-bottom: 4px;
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
  const authentication = useSelector(getAuthentication);
  const user = useSelector(getUser);
  const navigate = useNavigate();
  const location = useLocation();
  const [code, setCode] = useState("");
  const [error, setError] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [, bookmarkEmail] = useBookmarkedEmails();

  let { data: session, mutate: mutate } = useSWR("/api/session/");

  const isAuto = useMemo(
    () => !!location.state && location.state.auto === true,
    [location]
  );

  const handleCode = useCallback((e) => {
    setError({});
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
    if (!user || authentication < AUTHENTICATION.HARD) return;

    if (location.state) {
      location.state.email && bookmarkEmail(location.state.email);

      if (location.state.next) {
        if (getRouteByPathname(location.state.next)) {
          navigate(location.state.next);
        } else {
          window.location = location.state.next;
        }
        return;
      }
    }

    const route = routeConfig.tellMore.getLink();
    navigate(route);
  }, [authentication, user, bookmarkEmail, location, navigate]);

  return (
    <Container onSubmit={handleSubmit}>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>Un code de connexion vous a été envoyé par e-mail</h1>

      {location.state && location.state.code && (
        <LocalCode>{location.state.code}</LocalCode>
      )}

      {isAuto ? (
        <p style={{ marginTop: "2rem" }}>
          Validez le code de connexion qui vous a été envoyé par e-mail pour
          accéder à cette page
        </p>
      ) : (
        <>
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
        </>
      )}

      <Form>
        <TextField
          error={error && error.code}
          label="Code de connexion"
          onChange={handleCode}
          value={code}
          disabled={submitted}
          autoFocus
        />
        <Button
          block
          color="primary"
          disabled={submitted}
          style={{ height: 40 }}
        >
          Valider
        </Button>
      </Form>
    </Container>
  );
};

export default CodeConnexion;
