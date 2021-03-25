import React from "react";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import bgDesktop from "@agir/front/genericComponents/images/login_bg_desktop.svg";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const LeftBlock = styled.div`
  width: 524px;
  max-width: 40%;
  background-color: ${style.secondary100};
  position: relative;

  > :first-child {
    padding-bottom: calc(100vh - 213px);
  }

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const Title = styled.div`
  text-align: left;
  line-height: 1.625rem;
  padding-left: 93px;
  padding-right: 10px;
`;

const BackgroundDesktop = styled.div`
  position: absolute;
  bottom: 0px;
  left: 0px;
  width: 100%;
  height: calc(100vh - 213px);
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
      <div>
        <LogoAP
          style={{ marginTop: "38px", paddingLeft: "37px", width: "200px" }}
        />
        <Title>
          Le réseau social d’action pour la candidature{" "}
          <InlineBlock>de Jean-Luc Mélenchon pour 2022</InlineBlock>
        </Title>
      </div>
      <BackgroundDesktop />
    </LeftBlock>
  );
};

export default LeftBlockDesktop;
