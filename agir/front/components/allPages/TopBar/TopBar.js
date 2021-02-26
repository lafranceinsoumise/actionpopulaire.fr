import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getRoutes,
  getUser,
  getIsSessionLoaded,
  getBackLink,
  getTopBarRightLink,
} from "@agir/front/globalContext/reducers";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import MenuLink from "./MenuLink";
import Logo from "./Logo";
import RightLink from "./RightLink";
import SearchBar from "./SearchBar";

const TopBarBar = styled.div`
  position: fixed;
  top: 0;
  left: 0;

  z-index: ${style.zindexTopBar};

  width: 100%;
  padding: 0.75rem 2rem;

  background-color: #fff;
  box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 3px 2px rgba(0, 35, 44, 0.05);

  @media (max-width: ${+style.collapse - 1}px) {
    padding: 1rem 1.5rem;
  }
`;

const TopBarContainer = styled.div`
  display: flex;
  justify-content: space-between;

  max-width: 1320px;
  margin: 0 auto;

  & .large-only {
    @media only screen and (max-width: ${+style.collapse - 1}px) {
      display: none;
    }
  }

  & .small-only {
    @media only screen and (min-width: ${style.collapse}px) {
      display: none;
    }
  }

  .grow {
    flex-grow: 1;
  }

  .justify {
    justify-content: center;
  }
`;

const HorizontalFlex = styled.div`
  display: flex;
  align-items: center;

  & > * + * {
    margin-left: 1.25em;
  }
  & > .large-only + * {
    @media only screen and (max-width: ${+style.collapse - 1}px) {
      margin-left: 0;
    }
  }
  & > .small-only + * {
    @media only screen and (min-width: ${style.collapse}px) {
      margin-left: 0;
    }
  }
`;

export const TopBar = () => {
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const topBarRightLink = useSelector(getTopBarRightLink);

  return (
    <TopBarBar>
      <TopBarContainer>
        {isSessionLoaded ? (
          backLink ? (
            <MenuLink
              to={backLink.to}
              href={backLink.href}
              route={backLink.route}
              className="small-only"
              title={backLink.label}
              aria-label={backLink.label}
            >
              <FeatherIcon name="arrow-left" />
            </MenuLink>
          ) : (
            <MenuLink href={routes.search} className="small-only">
              <FeatherIcon name="search" />
            </MenuLink>
          )
        ) : null}
        <HorizontalFlex className="grow justify">
          <MenuLink href={routes.dashboard}>
            <Logo />
          </MenuLink>
          <form className="large-only grow" method="get" action={routes.search}>
            <SearchBar routes={routes} />
          </form>
        </HorizontalFlex>
        <PageFadeIn ready={isSessionLoaded}>
          <HorizontalFlex>
            <MenuLink href={routes.help} className="large-only">
              <FeatherIcon name="help-circle" />
              <span>Aide</span>
            </MenuLink>
            <RightLink
              settingsLink={(isSessionLoaded && topBarRightLink) || undefined}
              routes={routes}
              user={user}
            />
          </HorizontalFlex>
        </PageFadeIn>
      </TopBarContainer>
    </TopBarBar>
  );
};
TopBar.propTypes = {
  user: PropTypes.shape({
    displayName: PropTypes.string,
    isInsoumise: PropTypes.bool,
  }),
  routes: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.object,
      PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
          href: PropTypes.string,
        })
      ),
    ])
  ),
};
TopBar.defaultProps = {
  user: null,
  routes: {
    dashboard: "#dashboard",
    search: "#search",
    help: "#help",
    personalInformation: "#personalInformation",
    contactConfiguration: "#contactConfiguration",
    join: "#join",
    login: "#login",
  },
};

export default TopBar;
