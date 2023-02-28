import React from "react";
import Button from "@agir/front/genericComponents/Button";
import facebookImg from "@agir/front/genericComponents/images/facebook_circle.svg";
import styled from "styled-components";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

const ButtonFacebook = styled(Button)`
  width: 100%;
  margin-top: 20px;
`;

const LoginFacebook = (props) => {
  const routes = useSelector(getRoutes);

  return (
    <ButtonFacebook {...props} link color="choose" href={routes.facebookLogin}>
      <img src={facebookImg} width="24" height="24" />
      &nbsp; Connexion avec Facebook
    </ButtonFacebook>
  );
};

export default LoginFacebook;
