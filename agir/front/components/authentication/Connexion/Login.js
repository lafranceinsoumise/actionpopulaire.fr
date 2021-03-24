import React, { useEffect, useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import arrowRight from "@agir/front/genericComponents/images/arrow-right.svg";
import chevronDown from "@agir/front/genericComponents/images/chevron-down.svg";
import Toast from "@agir/front/genericComponents/Toast";
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

const ShowMore = styled.div`
  font-weight: 700;
  color: ${style.primary500};
  margin-top: 21px;
  cursor: pointer;
  display: inline-block;
  text-align: left;
`;

const ContainerConnexion = styled.div`
  width: 400px;
  max-width: 100%;
`;

const LoginMailButton = styled(Button)`
  margin-top: 0.5rem;
  margin-left: 0;
  max-width: 100%;
  width: 400px;
  justify-content: space-between;

  & + & {
    margin-left: 0;
  }
`;

const ToastNotConnected = () => {
  return <Toast>Vous devez vous connecter pour accéder à cette page</Toast>;
};

const Login = () => {
  const history = useHistory();
  const location = useLocation();
  const bookmarkedEmails = useBookmarkedEmails();
  const [showMore, setShowMore] = useState(false);
  const [error, setError] = useState(null);

  let next = "";
  if (location.state?.next) next = location.state.next;
  else if (location.search)
    next = new URLSearchParams(location.search).get("next");

  const handleShowMore = () => {
    setShowMore(true);
  };

  const loginBookmarkedMail = async (email) => {
    setError(null);
    const result = await login(email);
    if (result.error) {
      setError(result.error);
      return;
    }

    const route = routeConfig.codeLogin.getLink();
    history.push(route, {
      email: email,
      code: result.data && result.data.code,
      next: next,
    });
  };

  return (
    <ContainerConnexion>
      <h1>Je me connecte</h1>

      <BlockSwitchLink>
        <span>Pas encore de compte ?</span>
        &nbsp;
        <span>
          <Link route="signup">Je m'inscris</Link>
        </span>
      </BlockSwitchLink>

      {!!next && next.length > 0 && <ToastNotConnected />}

      {bookmarkedEmails[0].length > 0 && (
        <div style={{ marginTop: "1.5rem" }}>
          <span style={{ fontWeight: 500 }}>À mon compte :</span>

          {bookmarkedEmails[0].map((mail, id) => (
            <LoginMailButton
              key={id}
              color="primary"
              onClick={() => loginBookmarkedMail(mail)}
              block
              $block
            >
              {mail}
              <img src={arrowRight} style={{ color: "white" }} />
            </LoginMailButton>
          ))}
        </div>
      )}

      {error && !!error.detail && <Toast>{error.detail}</Toast>}

      {bookmarkedEmails[0].length > 0 &&
        (!showMore ? (
          <ShowMore onClick={handleShowMore}>
            Afficher tout <img src={chevronDown} alt="Afficher plus" />
          </ShowMore>
        ) : (
          <div
            style={{ textAlign: "center", marginTop: "20px", fontSize: "14px" }}
          >
            OU
          </div>
        ))}

      {(showMore || !(bookmarkedEmails[0].length > 0)) && <LoginMailEmpty />}

      <div style={{ textAlign: "center", margin: "20px", fontSize: "14px" }}>
        OU
      </div>
      <LoginFacebook />
    </ContainerConnexion>
  );
};

export default Login;
