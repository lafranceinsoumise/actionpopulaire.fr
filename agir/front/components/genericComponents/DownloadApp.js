import PropTypes from "prop-types";
import React from "react";
import styled, { useTheme } from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import logo from "@agir/front/genericComponents/logos/action-populaire_primary_mini.svg";

import { useDownloadBanner } from "@agir/front/app/hooks.js";
import { CONFIG } from "@agir/front/genericComponents/AppStore.js";
import { getMobileOS } from "@agir/front/authentication/common.js";

const StyledContainer = styled.div`
  display: flex;
  align-items: center;
  background-color: ${(props) => props.theme.primary500};
  color: ${(props) => props.theme.background0};
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
    color: ${(props) => props.theme.secondary500};
    font-weight: 700;
    font-size: 15px;
  }

  ${Description} {
    color: ${(props) => props.theme.background0};
    font-size: 12px;
    flex-wrap: wrap;
  }
`;

const Download = styled(Button)`
  background-color: ${(props) => props.theme.background0};
  color: ${(props) => props.theme.primary500};
  font-size: 13px;
  font-weight: 700;

  @media (max-width: 421px) {
    border-radius: 50px;
    width: 52px;
    height: 52px;
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

const AppLogo = styled.svg`
  width: 52px;
  height: 52px;

  @media (max-width: 350px) {
    display: none;
  }
`;

const OS = getMobileOS();

export const DownloadApp = ({ onClick }) => {
  const theme = useTheme();

  return (
    <StyledContainer>
      <div style={{ padding: "0.5rem", cursor: "pointer" }} onClick={onClick}>
        <StyledFeatherIcon
          name="x"
          color="${props => props.theme.background0}"
          width="0.5rem"
          height="0.5rem"
          small
        />
      </div>
      <AppLogo width="52" height="52" fill="none">
        <rect width="52" height="52" rx="11.056" fill={theme.secondary500} />
        <g clipPath="url(#a)">
          <path
            d="m29.419 42.449-8.052-8.024c-4.447-4.432-4.482-11.582-.078-15.971 4.404-4.39 11.58-4.354 16.026.077 4.447 4.432 4.482 11.582.078 15.971L29.42 42.45Z"
            fill={theme.background0}
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="m17.36 28.663 6.354 6.333 6.355-6.333a8.934 8.934 0 0 0 0-12.666c-3.51-3.497-9.2-3.497-12.71 0a8.934 8.934 0 0 0 0 12.666Zm6.354 10.16 8.276-8.246a11.634 11.634 0 0 0 0-16.494c-4.57-4.554-11.98-4.554-16.551 0a11.634 11.634 0 0 0 0 16.494l8.275 8.247Z"
            fill={theme.text1000}
          />
        </g>
        <defs>
          <clipPath id="a">
            <path
              fill={theme.background0}
              transform="translate(11.939 10.612)"
              d="M0 0h28.918v31.837H0z"
            />
          </clipPath>
        </defs>
      </AppLogo>
      <Content>
        <Title>ACTION POPULAIRE</Title>
        <Description>
          Téléchargez l’appli des actions près{" "}
          <InlineBlock>de chez vous</InlineBlock>
        </Description>
      </Content>
      <div style={{ paddingRight: "18px" }}>
        <Download
          link
          href={"iOS" === OS ? CONFIG.apple.href : CONFIG.google.href}
          aria-label="Télécharger"
        >
          <ResponsiveLayout
            breakpoint={421}
            MobileLayout={() => (
              <FeatherIcon name="download" color="primary500" />
            )}
            DesktopLayout={() => "Télécharger"}
          />
        </Download>
      </div>
    </StyledContainer>
  );
};

DownloadApp.propTypes = {
  onClick: PropTypes.func,
};

const ConnectedDownloadApp = () => {
  const [isBannerDownload, closeDownload] = useDownloadBanner();

  if (!isBannerDownload) return null;

  return <DownloadApp onClick={closeDownload} />;
};

export default ConnectedDownloadApp;
