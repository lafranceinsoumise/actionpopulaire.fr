import React from "react";
import Button from "@agir/front/genericComponents/Button";
import facebookImg from "@agir/front/genericComponents/images/facebook_circle.svg";
import styled from "styled-components";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

const ButtonFacebook = styled(Button)`
  width: 100%;
  margin-top: 20px;

  & > span {
    img {
      margin-top: -1px;
      margin-right: 0.5rem;
      background: radial-gradient(
        circle,
        ${(props) => props.theme.white} 0%,
        ${(props) => props.theme.white} 66%,
        transparent 66%,
        transparent
      );
      border-radius: 100%;

      @media (max-width: ${(props) => props.theme.collapseSmallMobile}px) {
        display: none;
      }
    }
  }
`;

const LoginFacebook = (props) => {
  const routes = useSelector(getRoutes);

  return (
    <ButtonFacebook {...props} link color="choose" href={routes.facebookLogin}>
      <img src={facebookImg} width="24" height="24" />
      Connexion avec Facebook
    </ButtonFacebook>
  );
};

export default LoginFacebook;
