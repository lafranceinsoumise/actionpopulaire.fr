import React from "react";
import styled, { useTheme } from "styled-components";

import LogoAP from "@agir/front/genericComponents/LogoAP";
import Link from "@agir/front/app/Link";

const LeftBlock = styled.div`
  width: 524px;
  max-width: 40%;
  background-color: ${(props) => props.theme.secondary100};
  position: relative;

  > :first-child {
    padding-bottom: calc(100vh - 213px);
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: none;
  }
`;

const Title = styled.div`
  text-align: left;
  line-height: 1.625rem;
  padding-left: 93px;
  padding-right: 10px;
`;

const BackgroundDesktop = styled.svg`
  position: absolute;
  bottom: 0px;
  left: 0px;
  width: 100%;
  height: 100vh - 213px;
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const LeftBlockDesktop = () => {
  const theme = useTheme();

  return (
    <LeftBlock>
      <div>
        <Link route="events">
          <LogoAP
            style={{ marginTop: "38px", paddingLeft: "37px", width: "200px" }}
          />
        </Link>
        <Title>
          Le réseau social d’action{" "}
          <InlineBlock>de la France insoumise</InlineBlock>
        </Title>
      </div>
      <BackgroundDesktop width="524" height="685" fill="none">
        <path
          fill={theme.primary500}
          d="M404.084 120.319 99.444 38.691 50.884 219.92l304.64 81.628z"
        />
        <path
          fill={theme.error500}
          d="m727.201 207.652-304.64-81.628-48.56 181.228 304.64 81.628zm-472.406 85.74-304.64-81.628-48.56 181.228 304.64 81.628z"
        />
        <path
          fill={theme.secondary500}
          d="m100.666 464.688-304.64-81.628-48.56 181.228 304.64 81.628zM83.113 34.313l-304.64-81.627-48.559 181.228 304.64 81.627zm665.619 604.999-304.64-81.628-48.56 181.228 304.64 81.628zM273.657 724.61l-304.64-81.628-48.56 181.228 304.64 81.628zm303.394-344.377-304.64-81.628-48.56 181.228 304.64 81.628z"
        />
        <path
          fill={theme.primary500}
          d="m428.213 553.429-304.64-81.628-48.56 181.228 304.64 81.628z"
        />
      </BackgroundDesktop>
    </LeftBlock>
  );
};

export default LeftBlockDesktop;
