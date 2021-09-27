import PropTypes from "prop-types";
import styled from "styled-components";

import { getIconDataUrl } from "@agir/front/genericComponents/Button/utils";
import Button from "@agir/front/genericComponents/Button";

import bgSmall from "./images/bg-small.svg";
import bgSeaSmall from "./images/bg-sea-small.jpg";
import bgLarge from "./images/bg-large.svg";
import bgSeaLarge from "./images/bg-sea-large.jpg";

export const Banner = styled.header`
  width: 100%;
  height: 166px;
  background-image: url(${bgSmall}), url(${bgSeaSmall});
  background-size: contain, cover;
  background-position: bottom center;
  background-repeat: no-repeat;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    height: 191px;
    background-image: url(${bgLarge}), url(${bgSeaLarge});
    background-size: 680px 158px, cover;
  }
`;

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
