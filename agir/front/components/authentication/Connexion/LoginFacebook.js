import React from "react";
import Button from "@agir/front/genericComponents/Button";
import facebookImg from "@agir/front/genericComponents/images/facebook_circle.svg";
import styled from "styled-components";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

const ButtonFacebook = styled(Button)`
  max-width: 100%;
  width: 100%;
  margin-top: 20px;
  justify-content: center;
  font-weight: normal;
  background-color: white;
  border: 1px solid #c4c4c4;
  transition: ease 0.2s;

  &:hover {
    background-color: #eee;
    border-color: #999;
  }

  img {
    width: 1.5rem;
    height: 1.5rem;
  }
`;

const LoginFacebook = () => {
  const routes = useSelector(getRoutes);

  return (
    <ButtonFacebook href={routes.facebookLogin} as={"a"}>
      <img src={facebookImg} width="24" height="24" />
      &nbsp; Connexion avec Facebook
    </ButtonFacebook>
  );
};

export default LoginFacebook;
