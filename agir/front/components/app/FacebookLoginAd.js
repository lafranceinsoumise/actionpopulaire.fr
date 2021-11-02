import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import Button from "@agir/front/genericComponents/Button";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { useMobileApp } from "@agir/front/app/hooks";

import facebookLogo from "@agir/front/genericComponents/logos/facebook.svg";
import facebookWhiteLogo from "@agir/front/genericComponents/logos/facebook_white.svg";

const FacebookLoginContainer = styled.div`
  background-color: #e8f2fe;
  max-width: 255px;
  border-radius: ${(props) => props.theme.borderRadius};
  padding: 24px;
  font-size: 14px;
  margin-bottom: 16px;
`;

const DismissMessage = styled.a`
  color: ${(props) => props.theme.black1000};
  text-decoration: underline;
  margin-top: 16px;

  &:hover {
    color: ${(props) => props.theme.black1000};
  }
`;

const FacebookLoginAd = () => {
  const [announcement, dismissCallback] =
    useCustomAnnouncement("facebook-login-ad");
  const { data: session } = useSWR("/api/session/");
  const { isIOS } = useMobileApp();

  return session && !session.facebookLogin && !isIOS && announcement ? (
    <FacebookLoginContainer>
      <img
        src={facebookLogo}
        width="32"
        height="32"
        style={{ height: "32px", marginBottom: "6px" }}
        alt="Facebook"
      />
      <h6>Facilitez vos prochaines connexions</h6>
      <p>
        Connectez votre compte à Facebook maintenant pour ne pas avoir à taper
        de code la prochaine fois.
      </p>
      <Button
        style={{ margin: "16px 0" }}
        small
        color="facebook"
        link
        route="facebookLogin"
      >
        <img
          style={{ height: "16px", marginRight: "5px" }}
          src={facebookWhiteLogo}
          width="16"
          height="16"
        />
        Connecter le compte
      </Button>
      <DismissMessage href="#" onClick={dismissCallback}>
        Ne plus afficher ce message
      </DismissMessage>
    </FacebookLoginContainer>
  ) : null;
};

export default FacebookLoginAd;
