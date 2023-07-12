import React, { useCallback, useMemo, useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import arrowRight from "@agir/front/genericComponents/images/arrow-right.svg";
import chevronDown from "@agir/front/genericComponents/images/chevron-down.svg";
import StaticToast from "@agir/front/genericComponents/StaticToast";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import LoginMailEmpty from "./LoginMailEmpty";
import LoginFacebook from "./LoginFacebook";
import Link from "@agir/front/app/Link";
import { BlockSwitchLink } from "@agir/front/authentication/Connexion/styledComponents";
import { login } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory, useLocation } from "react-router-dom";
import { useBookmarkedEmails } from "@agir/front/authentication/hooks";
import { useMobileApp } from "@agir/front/app/hooks";

const ShowMore = styled.div`
  font-weight: 700;
  color: ${style.primary500};
  margin-top: 21px;
  cursor: pointer;
  text-align: center;
`;

const ContainerConnexion = styled.div`
  max-width: 100%;
`;

const LoginMailButton = styled(Button)`
  margin-top: 0.5rem;
  justify-content: space-between;

  & > span {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const ToastNotConnected = () => {
  return (
    <StaticToast>
      Vous devez vous connecter pour accéder à cette page
    </StaticToast>
  );
};

const Login = () => {
  const history = useHistory();
  const location = useLocation();

  const { isMobileApp } = useMobileApp();
  const [bookmarkedEmails] = useBookmarkedEmails();

  const [showMore, setShowMore] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const next = useMemo(() => {
    if (location.state?.next) {
      return location.state.next;
    }
    if (location.search) {
      return new URLSearchParams(location.search).get("next");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleShowMore = useCallback(() => {
    setShowMore(true);
  }, []);

  const handleSubmit = useCallback(
    async (email) => {
      setIsLoading(true);
      setError(null);

      const result = await login(email);
      setIsLoading(false);

      if (result.error) {
        setError(result.error);
        return;
      }

      const route = routeConfig.codeLogin.getLink();
      history.push(route, {
        ...(location.state || {}),
        next,
        email: email,
        code: result.data && result.data.code,
      });
    },
    [next, history, location.state],
  );

  return (
    <ContainerConnexion>
      <h1>Je me connecte</h1>

      <BlockSwitchLink>
        <span>Pas encore de compte ?</span>
        &nbsp;
        <span>
          <Link route="signup" state={{ ...(location.state || {}), next }}>
            Je m'inscris
          </Link>
        </span>
      </BlockSwitchLink>

      {!!next && next.length > 0 && <ToastNotConnected />}

      {bookmarkedEmails.length > 0 && (
        <>
          <div style={{ marginTop: "1.5rem" }}>
            {bookmarkedEmails.map((email, id) => (
              <LoginMailButton
                key={id}
                color="primary"
                onClick={() => handleSubmit(email)}
                disabled={isLoading}
                block
              >
                <span>{email}</span>
                <img
                  src={arrowRight}
                  width="24"
                  height="24"
                  style={{ color: "white" }}
                />
              </LoginMailButton>
            ))}
          </div>
          <div
            style={{
              textAlign: "center",
              margin: "20px",
              marginBottom: "0",
              fontSize: "14px",
            }}
          >
            OU
          </div>

          {error && !!error.detail && (
            <StaticToast>
              {error.detail} <br />
              <Link route="codeLogin">
                Accéder à la page pour demander son code
              </Link>
            </StaticToast>
          )}
          {!isMobileApp && (
            <>
              <LoginFacebook disabled={isLoading} />
              <div
                style={{
                  textAlign: "center",
                  marginTop: "20px",
                  fontSize: "14px",
                }}
              >
                OU
              </div>
            </>
          )}

          {!showMore ? (
            <ShowMore onClick={handleShowMore}>
              Se connecter avec un autre{" "}
              <InlineBlock>
                e-mail{" "}
                <img
                  src={chevronDown}
                  width="24"
                  height="24"
                  alt="Afficher plus"
                />
              </InlineBlock>
            </ShowMore>
          ) : (
            <LoginMailEmpty
              onSubmit={handleSubmit}
              error={error}
              isLoading={isLoading}
            />
          )}
        </>
      )}

      {bookmarkedEmails.length === 0 && (
        <>
          <LoginMailEmpty
            onSubmit={handleSubmit}
            error={error}
            isLoading={isLoading}
          />
          {!isMobileApp && (
            <>
              <div
                style={{
                  textAlign: "center",
                  marginTop: "20px",
                  fontSize: "14px",
                }}
              >
                OU
              </div>
              <LoginFacebook />
            </>
          )}
        </>
      )}
    </ContainerConnexion>
  );
};

export default Login;
