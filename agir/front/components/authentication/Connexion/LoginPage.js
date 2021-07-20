import Helmet from "react-helmet";
import React, { useMemo } from "react";

import { Hide } from "@agir/front/genericComponents/grid";
import Login from "./Login";
import AutoLogin from "./AutoLogin";
import LeftBlockDesktop from "./LeftBlockDesktop";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import {
  MainBlock,
  Container,
  BackgroundMobile,
} from "./styledComponents";
import AuthenticatedLogin from "./AuthenticatedLogin";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getAuthentication,
  getUser,
  getIsSessionLoaded,
} from "@agir/front/globalContext/reducers";
import { AUTHENTICATION } from "@agir/front/authentication/common";

import logoMobile from "@agir/front/genericComponents/logos/action-populaire_mini.svg";

const LoginPage = () => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);
  const authentication = useSelector(getAuthentication);

  const autoLogin = useMemo(
    () =>
      (authentication === AUTHENTICATION.SOFT && user && user.email) || false,
    [authentication, user]
  );

  return (
    <>
      <Helmet>
        <meta name="title" content="Connexion" />
        <meta name="description" content="Connectez-vous à Action Populaire" />
      </Helmet>
      <PageFadeIn ready={isSessionLoaded}>
        {user && authentication === AUTHENTICATION.HARD ? (
          <AuthenticatedLogin user={user} />
        ) : autoLogin ? (
          <AutoLogin email={autoLogin} />
        ) : (
          <div style={{ display: "flex", minHeight: "100vh" }}>
            <LeftBlockDesktop />
            <MainBlock>
              <Container>
                <Hide over style={{ textAlign: "center", marginTop: "3rem" }}>
                  <img
                    src={logoMobile}
                    alt="logo"
                    width="70"
                    height="67"
                    style={{ width: "69px", marginBottom: "1.5rem" }}
                  />
                </Hide>

                <Login />
              </Container>

              <Hide over>
                <BackgroundMobile />
              </Hide>
            </MainBlock>
          </div>
        )}
      </PageFadeIn>
    </>
  );
};

export default LoginPage;
