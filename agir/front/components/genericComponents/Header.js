import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import FeatherIcon from "./FeatherIcon";
import Button from "./Button";

import style from "./style.scss";
import LogoFI from "@agir/front/genericComponents/LogoFI";

const HeaderBar = styled.div`
  position: fixed;
  top: 0;
  left: 0;

  z-index: 10;

  width: 100%;
  padding: 0.75em 2em; /* rem */

  background-color: #fff;
`;

const HeaderContainer = styled.div`
  display: flex;
  justify-content: space-between;

  max-width: 1400px;
  margin: 0 auto;

  .large-only {
    @media only screen and (max-width: 900px) {
      display: none;
    }
  }

  .small-only {
    @media only screen and (min-width: 901px) {
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

  * + * {
    margin-left: 1.25em;
  }
`;

const MenuLink = styled.a`
  display: flex;
  align-items: center;
  color: ${style.brandBlack};
  font-weight: 500;
  height: 3em; /* rem */

  * + * {
    margin-left: 0.5em;
  }

  :hover {
    text-decoration: none;
    color: ${style.brandBlack};
  }

  :hover > * {
    text-decoration: underline;
  }
`;

const SearchBar = styled.div`
  border: 1px ${style.grayLighter};
  position: relative;
  max-width: 450px;
`;

const SearchBarIndicator = styled.div`
  position: absolute;
  left: 1.5em; /* rem */
  top: 0.75em; /* rem */
`;

const SearchBarButton = styled.button.attrs(() => ({ type: "submit" }))`
  border: 0;
  background: none;
  position: absolute;
  right: 1.5em; /* rem */
  top: 0.75em; /* rem */
  display: none;

  input:focus + & {
    display: block;
  }
`;

const SearchBarInput = styled.input.attrs(() => ({ type: "text", name: "q" }))`
  width: 100%;
  height: 3em; /* rem */
  margin: 0;
  padding: 1px 3.5em; /* rem */

  border-radius: 0;
  background-color: ${style.grayLighter};
  color: ${style.brandBlack};
  border: 1px solid ${style.grayLighter};

  &::placeholder {
    color: ${style.gray};
  }
  &:focus {
    background: #fff;
    border: 1px solid ${style.gray};
  }
`;

const ConnectionInfo = ({ loggedAs, profileUrl, signInUrl, logInUrl }) =>
  loggedAs === undefined || loggedAs === "" ? (
    <>
      <MenuLink href={logInUrl}>
        <FeatherIcon name="user" />
        <span className="large-only">Connexion</span>
      </MenuLink>
      <Button color="secondary" href={signInUrl} className="large-only">
        Créer mon compte
      </Button>
    </>
  ) : (
    <MenuLink href={profileUrl}>
      <FeatherIcon name="user" />
      <span className="large-only">{loggedAs}</span>
    </MenuLink>
  );

ConnectionInfo.propTypes = {
  loggedAs: PropTypes.string,
  profileUrl: PropTypes.string,
  signInUrl: PropTypes.string,
  logInUrl: PropTypes.string,
};
ConnectionInfo.defaultProps = {
  profileUrl: "#",
  signInUrl: "#",
  logInUrl: "#",
};

const Header = ({
  loggedAs,
  dashboardUrl,
  searchUrl,
  helpUrl,
  profileUrl,
  signInUrl,
  logInUrl,
}) => {
  return (
    <HeaderBar>
      <HeaderContainer>
        <MenuLink href={searchUrl} className="small-only">
          <FeatherIcon name="search" />
        </MenuLink>

        <HorizontalFlex className="grow justify">
          <MenuLink href={dashboardUrl}>
            <LogoFI height="3em" />
          </MenuLink>
          <form className="large-only grow" method="post">
            <SearchBar method="post" action={searchUrl}>
              <SearchBarIndicator>
                <FeatherIcon
                  name="search"
                  color={style.gray}
                  alignOnText={false}
                />
              </SearchBarIndicator>
              <SearchBarInput placeholder="Rechercher un groupe ou un événement" />
              <SearchBarButton>
                <FeatherIcon
                  name="arrow-right"
                  color={style.gray}
                  alignOnText={false}
                />
              </SearchBarButton>
            </SearchBar>
          </form>
        </HorizontalFlex>
        <HorizontalFlex>
          <MenuLink href={helpUrl} className="large-only">
            <FeatherIcon name="help-circle" />
            <span>Aide</span>
          </MenuLink>
          <ConnectionInfo
            profileUrl={profileUrl}
            signInUrl={signInUrl}
            logInUrl={logInUrl}
            loggedAs={loggedAs}
          />
        </HorizontalFlex>
      </HeaderContainer>
    </HeaderBar>
  );
};
Header.propTypes = {
  loggedAs: PropTypes.string,
  dashboardUrl: PropTypes.string,
  searchUrl: PropTypes.string,
  helpUrl: PropTypes.string,
  profileUrl: PropTypes.string,
  signInUrl: PropTypes.string,
  logInUrl: PropTypes.string,
};
Header.defaultProps = {
  dashboardUrl: "#",
  searchUrl: "#",
  helpUrl: "#",
  profileUrl: "#",
  signInUrl: "#",
  logInUrl: "#",
};

export default Header;
