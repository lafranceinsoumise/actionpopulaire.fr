import React, { useCallback, useEffect } from "react";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import logo from "@agir/front/genericComponents/logos/action-populaire_primary_mini.svg";

import { useMobileApp } from "@agir/front/app/hooks.js";
import { CONFIG } from "@agir/front/genericComponents/AppStore.js";
import { getMobileOS } from "@agir/front/authentication/common.js";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import {
  setBannerDownload,
  clearBannerDownload,
} from "@agir/front/globalContext/actions";
import { getIsBannerDownload } from "@agir/front/globalContext/reducers";

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

const OS = getMobileOS();
const BANNER_ID = "BANNER_download_closed";

export const DownloadApp = () => {
  const { isMobileApp } = useMobileApp();

  const dispatch = useDispatch();
  const isBannerDownload = useSelector(getIsBannerDownload);

  const closeDownload = useCallback(() => {
    dispatch(clearBannerDownload());
    window.localStorage.setItem(BANNER_ID, 1);
  }, [dispatch]);

  useEffect(() => {
    let bannerClosed = window.localStorage.getItem(BANNER_ID);
    bannerClosed = !isNaN(parseInt(bannerClosed)) ? parseInt(bannerClosed) : 0;
    let visitCount = window.localStorage.getItem("AP_vcount");
    visitCount = !isNaN(parseInt(visitCount)) ? parseInt(visitCount) : 0;

    if (visitCount % 2 === 0) {
      window.localStorage.setItem(BANNER_ID, 0);
      dispatch(setBannerDownload());
    } else {
      if (!bannerClosed) {
        dispatch(setBannerDownload());
      }
    }
  }, []);

  if (isMobileApp) return null;

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
