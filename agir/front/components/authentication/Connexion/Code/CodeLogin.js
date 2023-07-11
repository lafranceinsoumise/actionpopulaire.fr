import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useHistory, useLocation } from "react-router-dom";
import styled from "styled-components";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import TextField from "@agir/front/formComponents/TextField";

import { checkCode } from "@agir/front/authentication/api";
import { routeConfig, getRouteByPathname } from "@agir/front/app/routes.config";
import { useBookmarkedEmails } from "@agir/front/authentication/hooks";

import { AUTHENTICATION } from "@agir/front/authentication/common";

const DEFAULT_NEXT_PAGE = routeConfig.tellMore.getLink();

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
  cursor: pointer;
  padding: 1rem 2rem;
  margin: 0;
  margin-top: 1rem;
  background-color: ${style.green100};
`;

const CodeConnexion = () => {
  const history = useHistory();
  const location = useLocation();
  const [code, setCode] = useState("");
  const [error, setError] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [, bookmarkEmail] = useBookmarkedEmails();

  const shouldBeConnected = useRef(false);

  const { data: session } = useSWR("/api/session/");
  const { trigger: mutate } = useSWRMutation("/api/session/");

  const isAuto = useMemo(
    () => !!location.state && location.state.auto === true,
    [location],
  );

  const handleCode = useCallback((e) => {
    setError({});
    setCode(e.target.value);
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setIsLoading(true);
      setError({});
      const data = await checkCode(code);
      setIsLoading(false);

      if (data.error) {
        setError(data.error);
        return;
      }

      if (shouldBeConnected.current === false) {
        mutate();
        shouldBeConnected.current = true;
      } else {
        // Force refresh if first submit session call has not been fired
        // (ex. first time opening on iPad)
        window.location = DEFAULT_NEXT_PAGE;
      }
    },
    [code, mutate],
  );

  useEffect(() => {
    if (!session?.user || session?.authentication < AUTHENTICATION.HARD) return;

    if (location.state) {
      location.state.email && bookmarkEmail(location.state.email);

      if (location.state.next) {
        if (getRouteByPathname(location.state.next)) {
          history.push(location.state.next);
        } else {
          window.location = location.state.next;
        }
        return;
      }
    }

    history.push(DEFAULT_NEXT_PAGE);
  }, [session, bookmarkEmail, location, history]);

  return (
    <Container onSubmit={handleSubmit}>
      <RawFeatherIcon name="mail" width="41px" height="41px" />

      <h1>Un code de connexion vous a été envoyé par e-mail</h1>

      {location.state && location.state.code && (
        <LocalCode onDoubleClick={() => setCode(location.state.code)}>
          {location.state.code}
        </LocalCode>
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
          disabled={isLoading}
          autoFocus
        />
        <Button
          type="submit"
          block
          color="primary"
          disabled={isLoading}
          loading={isLoading}
          style={{ height: 40 }}
        >
          Valider
        </Button>
      </Form>
    </Container>
  );
};

export default CodeConnexion;
