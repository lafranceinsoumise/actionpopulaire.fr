import React from "react";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import logo from "@agir/front/genericComponents/logos/action-populaire_primary_mini.svg";

import { useDownloadBanner } from "@agir/front/app/hooks.js";
import { CONFIG } from "@agir/front/genericComponents/AppStore.js";
import { getMobileOS } from "@agir/front/authentication/common.js";

const StyledContainer = styled.div`
  display: flex;
  align-items: center;
  background-color: ${style.primary500};
  color: #fff;
  justify-content: space-evenly;
  height: 80px;
`;

const Title = styled.div``;
const Description = styled.div``;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  padding: 12px;

  ${Title} {
    color: ${style.secondary500};
    font-weight: 700;
    font-size: 15px;
  }

  ${Description} {
    color: #fff;
    font-size: 12px;
    flex-wrap: wrap;
  }
`;

const DownloadMinus = styled(Button)`
  border-radius: 50px;
  background-color: #fff;
  width: 52px;
  height: 52px;
  color: ${style.primary500};
  font-size: 13px;
  font-weight: 700;
  justify-content: center;

  @media (min-width: 422px) {
    display: none;
  }
`;

const Download = styled(Button)`
  background-color: #fff;
  color: ${style.primary500};
  font-size: 13px;
  font-weight: 700;
  justify-content: center;

  @media (max-width: 421px) {
    display: none;
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const StyledFeatherIcon = styled(FeatherIcon)`
  &:hover {
    cursor: pointer;
  }
`;

const AppLogo = styled.img`
  width: 52px;
  height: 52px;

  @media (max-width: 350px) {
    display: none;
  }
`;

const OS = getMobileOS();

export const DownloadApp = () => {
  const [isBannerDownload, closeDownload] = useDownloadBanner();

  if (!isBannerDownload) return null;

  return (
    <StyledContainer>
      <div
        style={{ padding: "0.5rem", cursor: "pointer" }}
        onClick={closeDownload}
      >
        <StyledFeatherIcon
          name="x"
          color="#fff"
          width="0.5rem"
          height="0.5rem"
          small
        />
      </div>
      <AppLogo src={logo} width="52" height="52" alt="Logo Action Populaire" />
      <Content>
        <Title>ACTION POPULAIRE</Title>
        <Description>
          Téléchargez l’appli des actions près{" "}
          <InlineBlock>de chez vous</InlineBlock>
        </Description>
      </Content>
      <div style={{ paddingRight: "18px" }}>
        <DownloadMinus
          as="a"
          href={"iOS" === OS ? CONFIG.apple.href : CONFIG.google.href}
        >
          <FeatherIcon name="download" color={style.primary500} />
        </DownloadMinus>
        <Download
          as="a"
          href={"iOS" === OS ? CONFIG.apple.href : CONFIG.google.href}
        >
          Télécharger
        </Download>
      </div>
    </StyledContainer>
  );
};

export default DownloadApp;
