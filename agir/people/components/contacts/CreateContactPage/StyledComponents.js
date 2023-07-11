import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { getIconDataUrl } from "@agir/front/genericComponents/Button/utils";
import Button from "@agir/front/genericComponents/Button";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
import { useImageLoad } from "@agir/lib/utils/hooks";

import bgSmall from "./images/bg-small.png";
import bgSeaSmall from "./images/bg-sea-small.jpg";
import bgLarge from "./images/bg-large.png";
import bgSeaLarge from "./images/bg-sea-large.jpg";

const StyledBanner = styled.header`
  width: 100%;
  height: 166px;
  background-image: url(${bgSmall}), url(${bgSeaSmall});
  background-size: contain, cover;
  background-position: center center;
  background-repeat: no-repeat;
  opacity: ${({ $isReady }) => ($isReady ? 1 : 0)};
  transition: opacity 300ms ease-in;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    height: 191px;
    background-position: bottom center;
    background-image: url(${bgLarge}), url(${bgSeaLarge});
    background-size:
      680px 158px,
      cover;
  }
`;

export const Banner = (props) => {
  const bg = useResponsiveMemo(bgSmall, bgLarge);
  const bgSea = useResponsiveMemo(bgSeaSmall, bgSeaLarge);
  const bgReady = useImageLoad(bg);
  const bgSeaReady = useImageLoad(bgSea);

  return <StyledBanner {...props} $isReady={!!bgReady && !!bgSeaReady} />;
};

export const BackButton = styled(Button).attrs((props) => ({
  ...props,
  icon: "arrow-left",
  children: props.children || "Retour",
}))`
  &,
  &:hover,
  &:focus,
  &:active {
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.7;
    text-transform: uppercase;
    padding-left: 0;
    padding-right: 0;
    color: #585858;
    background-color: transparent;
    border-color: transparent;
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    opacity: 0.75;
    text-decoration: none;
    cursor: default;
  }

  &:hover,
  &:focus,
  &:active {
    text-decoration: underline;
  }

  &:before {
    background-image: ${getIconDataUrl({ color: "#585858" })};
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;

export const PageContent = styled.main`
  margin: 0 auto;
  max-width: 680px;
  padding: 0 3.25rem 3.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1.5rem;
  }
`;
