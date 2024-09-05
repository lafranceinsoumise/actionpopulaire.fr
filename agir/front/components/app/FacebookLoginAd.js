import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import Button from "@agir/front/genericComponents/Button";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { useMobileApp } from "@agir/front/app/hooks";

import facebookLogo from "@agir/front/genericComponents/logos/facebook.svg";
import facebookWhiteLogo from "@agir/front/genericComponents/logos/facebook_white.svg";

const FacebookLoginContainer = styled.div`
  background-color: ${(props) => props.theme.facebookLight};
  color: ${(props) => props.theme.black};
  max-width: 15.9375rem;
  border-radius: ${(props) => props.theme.borderRadius};
  padding: 1.5rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;

  h6 {
    color: inherit;
  }
`;

const DismissMessage = styled.a`
  color: ${(props) => props.theme.black};
  text-decoration: underline;
  margin-top: 1rem;

  &:hover {
    color: ${(props) => props.theme.black};
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
