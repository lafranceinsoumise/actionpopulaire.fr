import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import FeatherIcon from "./FeatherIcon";
import Button from "./Button";

import style from "./style.scss";
import LogoFI from "@agir/front/genericComponents/LogoFI";

const MenuLink = styled.a`
  display: flex;
  align-items: center;
  margin: 0 1em;
  color: ${style.brandBlack};
  font-weight: 500;
  height: 3rem;

  * + * {
    margin-left: 1em;
  }

  :hover {
    text-decoration: none;
    color: ${style.brandBlack};
  }

  :hover > * {
    text-decoration: underline;
  }
`;

const HeaderBar = styled.div`
  position: fixed;
  top: 0;
  left: 0;

  width: 100%;
  padding: 10px 30px;

  background-color: #fff;
`;

const HeaderContainer = styled.div`
  display: flex;
  justify-content: space-between;

  max-width: 1400px;
  margin: 0 auto;
`;

const HorizontalFlex = styled.div`
  display: flex;
  align-items: center;
`;

const SearchMenu = styled(MenuLink)`
  display: none;

  @media only screen and (max-width: 900px) {
    display: flex;
  }
`;

const SearchBar = styled.form`
  border: 1px ${style.grayLighter};
  position: relative;
  margin: 0 1em;

  @media only screen and (max-width: 900px) {
    display: none;
  }
`;

const SearchBarIndicator = styled.div`
  position: absolute;
  left: 1.5rem;
  top: 0.75rem;
`;

const SearchBarButton = styled.button.attrs(() => ({ type: "submit" }))`
  border: 0;
  background: none;
  position: absolute;
  right: 1.5rem;
  top: 0.75rem;
  display: none;

  input:focus + & {
    display: block;
  }
`;

const SearchBarInput = styled.input.attrs(() => ({ type: "text" }))`
  min-width: 450px;
  height: 3rem;
  padding: 1px 3.5rem;

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

const BigScreenOnly = styled.div`
  @media only screen and (max-width: 900px) {
    display: none;
  }
`;

const ConnectionInfo = ({ loggedAs, profileUrl, signInUrl, logInUrl }) =>
  loggedAs === undefined || loggedAs === "" ? (
    <>
      <MenuLink href={logInUrl}>
        <FeatherIcon name="user" />
        <BigScreenOnly>Connexion</BigScreenOnly>
      </MenuLink>
      <BigScreenOnly>
        <Button color="secondary" href={signInUrl}>
          Créer mon compte
        </Button>
      </BigScreenOnly>
    </>
  ) : (
    <MenuLink href={profileUrl}>
      <FeatherIcon name="user" />
      <BigScreenOnly>{loggedAs}</BigScreenOnly>
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

const Header = ({ loggedAs }) => {
  return (
    <HeaderBar>
      <HeaderContainer>
        <SearchMenu href="#">
          <FeatherIcon name="search" />
        </SearchMenu>

        <HorizontalFlex>
          <LogoFI height="48px" />
          <SearchBar>
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
        </HorizontalFlex>
        <HorizontalFlex>
          <BigScreenOnly>
            <MenuLink href="#">
              <FeatherIcon name="help-circle" />
              <span>Aide</span>
            </MenuLink>
          </BigScreenOnly>
          <ConnectionInfo
            profileUrl="#"
            signInUrl="#"
            logInUrl="#"
            loggedAs={loggedAs}
          />
        </HorizontalFlex>
      </HeaderContainer>
    </HeaderBar>
  );
};
Header.propTypes = {
  loggedAs: PropTypes.string,
};

export default Header;
