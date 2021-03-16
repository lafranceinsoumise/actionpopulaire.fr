import React from "react";
import Button from "@agir/front/genericComponents/Button";
import facebookImg from "@agir/front/genericComponents/images/facebook_circle.svg";
import styled from "styled-components";

const ButtonFacebook = styled(Button)`
  &:hover {
    backgorund-color: #eee;
  }
  max-width: 100%;
  width: 400px;
  justify-content: center;
  font-weight: normal;
  background-color: white;
  border: 1px solid #c4c4c4;
  transition: ease 0.2s; ;
`;

const LoginFacebook = () => {
  const handleLoginFacebook = () => {
    console.log("login with facebook");
  };

  return (
    <ButtonFacebook onClick={handleLoginFacebook}>
      <img src={facebookImg} style={{ width: "24px", height: "24px" }} />
      &nbsp; Connexion avec Facebook
    </ButtonFacebook>
  );
};

export default LoginFacebook;
