import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Announcements from "@agir/front/dashboardComponents/Announcements";
import Button from "@agir/front/genericComponents/Button";
import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Footer from "@agir/front/dashboardComponents/Footer";
import Navigation, {
  SecondaryNavigation,
} from "@agir/front/dashboardComponents/Navigation";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";
import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { useMobileApp } from "@agir/front/app/hooks";

import facebookLogo from "@agir/front/genericComponents/logos/facebook.svg";
import facebookWhiteLogo from "@agir/front/genericComponents/logos/facebook_white.svg";

export const LayoutSubtitle = styled.h2`
  color: ${style.black700};
  font-weight: 400;
  font-size: 14px;
  margin: 8px 0;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

export const LayoutTitle = styled.h1`
  display: flex;
  align-items: center;
  font-size: 26px;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const FixedColumn = styled(Column)`
  position: relative;
  z-index: ${style.zindexMainContent};

  @media (min-width: ${style.collapse}px) {
    position: sticky;
    top: 72px;
    padding-top: 72px;
  }
`;

const Banner = styled.div`
  width: 100%;
  padding: 1rem 0 0;
  background-color: ${({ smallBackgroundColor }) =>
    smallBackgroundColor || "transparent"};

  &:empty {
    display: none;
  }

  @media (min-width: ${style.collapse}px) {
    display: none;
  }
`;

const SidebarColumn = styled(Column)`
  padding-top: 72px;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const MainColumn = styled(Column)`
  padding-top: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 0;
  }
`;

const MainContainer = styled(Container)`
  padding-bottom: 72px;

  @media (min-width: ${style.collapse}px) {
    & > ${Row} {
      flex-wrap: nowrap;
    }
  }

  @media (max-width: ${style.collapse}px) {
    padding-top: 24px;
    padding-bottom: 24px;
    background-color: ${({ smallBackgroundColor }) =>
      smallBackgroundColor || "transparent"};
  }
`;

const FacebookLoginContainer = styled.div`
  background-color: #e8f2fe;
  max-width: 255px;
  border-radius: 8px;
  padding: 24px;
  font-size: 14px;
  margin-bottom: 16px;
`;

const DismissMessage = styled.a`
  &:hover {
    color: ${style.black1000};
  }
  color: ${style.black1000};
  text-decoration: underline;
  margin-top: 16px;
`;

const FacebookLoginAd = () => {
  const routes = useSelector(getRoutes);
  const [announcement, dismissCallback] = useCustomAnnouncement(
    "facebook-login-ad"
  );
  const { data: session } = useSWR("/api/session/");
  const { isIOS } = useMobileApp();

  return session && !session.facebookLogin && !isIOS && announcement ? (
    <FacebookLoginContainer>
      <img
        src={facebookLogo}
        style={{ height: "32px", marginBottom: "6px" }}
        alt="Facebook"
      />
      <h6>Facilitez vos prochaines connexions</h6>
      <p>
        Connectez votre compte à Facebook maintenant pour ne pas avoir à taper
        de code la prochaine fois.
      </p>
      <Button
        style={{ margin: "16px 0" }}
        small
        $background="#1778f2"
        $hoverBackground="#1778f2"
        $labelColor="#fff"
        as="a"
        href={routes.facebookLogin}
      >
        <img
          style={{ height: "16px", marginRight: "5px" }}
          src={facebookWhiteLogo}
        />
        Connecter le compte
      </Button>
      <DismissMessage href="#" onClick={dismissCallback}>
        Ne plus afficher ce message
      </DismissMessage>
    </FacebookLoginContainer>
  ) : null;
};

const Layout = (props) => (
  <>
    {props.hasBanner ? (
      <Banner {...props}>
        <Announcements displayType="banner" />
      </Banner>
    ) : null}
    <MainContainer {...props}>
      <Row gutter={50} align="flex-start">
        <FixedColumn width="320px">
          <Navigation {...props} />
        </FixedColumn>
        <MainColumn grow>
          <section>
            {props.title ? (
              <header>
                <LayoutTitle>{props.title}</LayoutTitle>
                <LayoutSubtitle>{props.subtitle}</LayoutSubtitle>
              </header>
            ) : null}
            {props.children}
          </section>
        </MainColumn>
        <SidebarColumn>
          <FacebookLoginAd />
          <Announcements displayType="sidebar" />
          <SecondaryNavigation />
        </SidebarColumn>
      </Row>
    </MainContainer>
    <Footer
      desktopOnly={props.desktopOnlyFooter}
      displayOnMobileApp={props.displayFooterOnMobileApp}
    />
  </>
);

export default Layout;

Layout.propTypes = {
  active: PropTypes.string,
  routes: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
          href: PropTypes.string,
        })
      ),
    ])
  ),
  title: PropTypes.string,
  subtitle: PropTypes.string,
  children: PropTypes.node,
  desktopOnlyFooter: PropTypes.bool,
  hasBanner: PropTypes.bool,
  displayFooterOnMobileApp: PropTypes.bool,
};
Layout.defaultProps = {
  routes: {
    events: "/evenements",
    groups: "/mes-groupes",
    activity: "/activite",
  },
  desktopOnlyFooter: true,
  hasBanner: false,
  displayFooterOnMobileApp: false,
};
