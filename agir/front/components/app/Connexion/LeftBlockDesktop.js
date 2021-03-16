import React from "react";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import bgDesktop from "@agir/front/genericComponents/images/login_bg_desktop.svg";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const LeftBlock = styled.div`
  width: 40%;
  background-color: ${style.secondary100};
  position: relative;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const Title = styled.div`
  text-align: center;
  div {
    display: inline-block;
    text-align: left;
    line-height: 21px;
    max-width: 350px;
  }
`;

const BackgroundDesktop = styled.div`
  position: absolute;
  bottom: 0px;
  left: 0px;
  width: 100%;
  height: 450px;
  background-image: url(${bgDesktop});
  background-size: cover;
  background-repeat: no-repeat;
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const LeftBlockDesktop = () => {
  return (
    <LeftBlock>
      <div style={{ padding: "37px", paddingBottom: "450px" }}>
        <LogoAP style={{ width: "200px" }} />
        <Title>
          <div>
            Le réseau social d’action pour la candidature de Jean-Luc Mélenchon{" "}
            <InlineBlock>pour 2022</InlineBlock>
          </div>
        </Title>
      </div>
      <BackgroundDesktop />
    </LeftBlock>
  );
};

export default LeftBlockDesktop;
