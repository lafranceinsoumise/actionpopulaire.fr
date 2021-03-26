import React from "react";

import { Hide } from "@agir/front/genericComponents/grid";
import Login from "./Login";
import LeftBlockDesktop from "./LeftBlockDesktop";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import { MainBlock, Container, BackgroundMobile } from "./styledComponents";
import AuthenticatedLogin from "./AuthenticatedLogin";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getUser,
  getIsSessionLoaded,
} from "@agir/front/globalContext/reducers";

import logoMobile from "@agir/front/genericComponents/logos/action-populaire_mini.svg";

const LoginPage = () => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);

  return (
    <PageFadeIn ready={isSessionLoaded}>
      {user ? (
        <AuthenticatedLogin user={user} />
      ) : (
        <div style={{ display: "flex", minHeight: "100vh" }}>
          <LeftBlockDesktop />
          <MainBlock>
            <Container>
              <Hide over style={{ textAlign: "center", marginTop: "3rem" }}>
                <img
                  src={logoMobile}
                  alt="logo"
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
  );
};

export default LoginPage;
