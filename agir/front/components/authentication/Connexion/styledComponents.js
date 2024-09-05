import React from "react";
import styled, { useTheme } from "styled-components";

export const MainBlock = styled.div`
  width: calc(100% - 500px);
  min-width: 60%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  h1 {
    margin: 0px;
    font-weight: 700;
    font-size: 40px;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
    min-height: 100vh;
    display: block;
    text-align: center;

    h1 {
      font-size: 28px;
      text-align: center;
    }

    .mobile-center {
      text-align: center;
    }
  }
`;

export const Container = styled.div`
  display: inline-block;
  text-align: left;
  width: 500px;
  max-width: 100%;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding-bottom: 150px;
    padding-left: 2rem;
    padding-right: 2rem;
  }
`;

export const BackgroundMobile = styled((props) => {
  const theme = useTheme();

  return (
    <svg width="420" height="160" viewBox="0 0 420 160" fill="none" {...props}>
      <path
        fill={theme.primary500}
        d="m281.412 84.234-153.11-41.253-24.407 91.59 153.111 41.253z"
      />
      <path
        fill={theme.error500}
        d="M443.81 128.371 290.7 87.118l-24.407 91.589 153.111 41.253zm-237.431 43.332L53.269 130.45l-24.407 91.589 153.111 41.253z"
      />
      <path
        fill={theme.secondary500}
        d="M120.093 40.769-33.017-.484l-24.407 91.589 153.111 41.253z"
      />
      <path
        fill={theme.primary500}
        d="m45.287 128.299-153.11-41.253-24.407 91.589 153.111 41.253z"
      />
    </svg>
  );
})`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100vw;
  height: auto;
`;

export const BlockSwitchLink = styled.div`
  margin-top: 0.5rem;
  display: inline-block;
  text-align: left;

  span:nth-child(2) {
    color: ${(props) => props.theme.primary500};
    font-weight: 700;
    display: inline-block;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    text-align: center;
    width: 100%;
  }
`;
