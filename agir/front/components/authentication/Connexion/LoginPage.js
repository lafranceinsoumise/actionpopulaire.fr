import React, { useEffect, useMemo } from "react";
import { useHistory } from "react-router-dom";

import { Hide } from "@agir/front/genericComponents/grid";
import { IconLogo } from "@agir/front/genericComponents/LogoAP";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import AuthenticatedLogin from "./AuthenticatedLogin";
import AutoLogin from "./AutoLogin";
import LeftBlockDesktop from "./LeftBlockDesktop";
import Login from "./Login";
import { BackgroundMobile, Container, MainBlock } from "./styledComponents";

import { AUTHENTICATION } from "@agir/front/authentication/common";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getAuthentication,
  getIsSessionLoaded,
  getUser,
} from "@agir/front/globalContext/reducers";

const LoginPage = () => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);
  const authentication = useSelector(getAuthentication);
  const history = useHistory();

  const autoLogin = useMemo(
    () =>
      (authentication === AUTHENTICATION.SOFT && user && user.email) || false,
    [authentication, user],
  );

  useEffect(() => {
    const searchParams = new URLSearchParams(history.location.search);
    searchParams.delete("meta_title");
    searchParams.delete("meta_description");
    searchParams.delete("meta_image");
    history.replace({ search: searchParams.toString() });
  }, [history]);

  return (
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
              <Hide $over style={{ textAlign: "center", marginTop: "3rem" }}>
                <IconLogo style={{ width: "69px", marginBottom: "1.5rem" }} />
              </Hide>
              <Login />
            </Container>
            <Hide $over>
              <BackgroundMobile />
            </Hide>
          </MainBlock>
        </div>
      )}
    </PageFadeIn>
  );
};

export default LoginPage;
