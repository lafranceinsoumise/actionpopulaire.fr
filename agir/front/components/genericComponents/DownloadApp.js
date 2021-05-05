import React, { useCallback } from "react";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import logo from "@agir/front/genericComponents/logos/action-populaire_primary_mini.svg";

import { useMobileApp } from "@agir/front/app/hooks.js";
import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { CONFIG } from "@agir/front/genericComponents/AppStore.js";

const StyledContainer = styled.div`
  display: flex;
  align-items: center;
  background-color: ${style.primary500};
  color: #fff;
  justify-content: space-evenly;
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

  @media (min-width: 380px) {
    display: none;
  }
`;

const Download = styled(Button)`
  background-color: #fff;
  color: ${style.primary500};
  font-size: 13px;
  font-weight: 700;
  justify-content: center;

  @media (max-width: 380px) {
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

export const DownloadApp = () => {
  const { isMobileApp, isIOS } = useMobileApp();
  const [hasBannerDownload, dismissBannerDownload] = useCustomAnnouncement(
    "bannerDownload"
  );

  const dismissDownload = useCallback(async () => {
    await dismissBannerDownload();
  }, [dismissBannerDownload]);

  if (isMobileApp) return null;

  if (!hasBannerDownload) return null;

  return (
    <StyledContainer>
      <div
        style={{ padding: "0.5rem", cursor: "pointer" }}
        onClick={dismissDownload}
      >
        <StyledFeatherIcon
          name="x"
          color="#fff"
          width="0.5rem"
          height="0.5rem"
          small
        />
      </div>
      <img src={logo} alt="Logo" style={{ width: "52px", height: "52px" }} />
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
          href={isIOS ? CONFIG.apple.href : CONFIG.google.href}
        >
          <FeatherIcon name="download" color={style.primary500} />
        </DownloadMinus>
        <Download as="a" href={isIOS ? CONFIG.apple.href : CONFIG.google.href}>
          Télécharger
        </Download>
      </div>
    </StyledContainer>
  );
};

export default DownloadApp;
