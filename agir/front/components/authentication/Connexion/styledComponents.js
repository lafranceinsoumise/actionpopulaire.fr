import styled from "styled-components";
import * as style from "@agir/front/genericComponents/_variables.scss";
import bgMobile from "@agir/front/genericComponents/images/login_bg_mobile.svg";

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

  @media (max-width: ${style.collapse}px) {
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

  @media (max-width: ${style.collapse}px) {
    padding-bottom: 150px;
    padding-left: 2rem;
    padding-right: 2rem;
  }
`;

export const BackgroundMobile = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 150px;
  background-image: url(${bgMobile});
  background-size: cover;
  background-repeat: no-repeat;
`;

export const BlockSwitchLink = styled.div`
  margin-top: 0.5rem;
  display: inline-block;
  text-align: left;

  span:nth-child(2) {
    color: ${style.primary500};
    font-weight: 700;
    display: inline-block;
  }

  @media (max-width: ${style.collapse}px) {
    text-align: center;
    width: 100%;
  }
`;
