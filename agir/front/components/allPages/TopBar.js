import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import FeatherIcon from "../genericComponents/FeatherIcon";
import Button from "../genericComponents/Button";

import style from "@agir/front/genericComponents/_variables.scss";
import LogoFI from "../genericComponents/LogoFI";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";

const TopBarBar = styled.div`
  position: fixed;
  top: 0;
  left: 0;

  z-index: 10;

  width: 100%;
  padding: 0.75rem 2rem;

  background-color: #fff;
  box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 3px 2px rgba(0, 35, 44, 0.05);
`;

const TopBarContainer = styled.div`
  display: flex;
  justify-content: space-between;

  max-width: 1400px;
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

  * + * {
    margin-left: 1.25em;
  }
`;

const MenuLink = styled.a`
  display: flex;
  align-items: center;
  color: ${style.black1000};
  font-weight: 500;
  height: 3rem;

  * + * {
    margin-left: 0.5em;
  }

  :hover {
    text-decoration: none;
    color: ${style.black1000};
  }

  :hover > * {
    text-decoration: underline;
  }
`;

const SearchBar = styled.div`
  position: relative;
  max-width: 450px;
`;

const SearchBarIndicator = styled.div`
  position: absolute;
  left: 1rem;
  top: 0.75rem;
`;

const SearchBarButton = styled.button.attrs(() => ({ type: "submit" }))`
  position: absolute;
  right: 1em;
  top: 0.75rem;

  padding: 0;
  width: 1.5rem;

  border: 0;
  background: none;

  svg {
    display: none;
  }

  input:focus + & svg {
    display: block;
  }
`;

const SearchBarInput = styled.input.attrs(() => ({ type: "text", name: "q" }))`
  width: 100%;
  height: 3rem;
  margin: 0;
  padding: 0 3.5rem;

  border-radius: 3px;
  background-color: ${style.black50};
  color: ${style.black1000};
  border: 1px solid ${style.black50};

  &::placeholder {
    color: ${style.black500};
    font-weight: 500;
    opacity: 1;
  }
  &:focus {
    background: #fff;
    border: 1px solid ${style.black500};
  }
`;

const ConnectionInfo = ({ user, routes }) =>
  user === null ? (
    <>
      <MenuLink href={routes.logIn}>
        <FeatherIcon name="user" />
        <span className="large-only">Connexion</span>
      </MenuLink>
      <Button color="secondary" href={routes.signIn} className="large-only">
        Créer mon compte
      </Button>
    </>
  ) : (
    <MenuLink
      href={
        user.isInsoumise
          ? routes.personalInformation
          : routes.contactConfiguration
      }
    >
      <FeatherIcon name="user" />
      <span className="large-only">{user.displayName}</span>
    </MenuLink>
  );

ConnectionInfo.propTypes = {
  user: PropTypes.shape({
    displayName: PropTypes.string,
    isInsoumise: PropTypes.bool,
  }),
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
};

export const PureTopBar = ({ user, routes }) => {
  const inputRef = React.useRef();

  return (
    <TopBarBar>
      <TopBarContainer>
        <MenuLink href={routes.search} className="small-only">
          <FeatherIcon name="search" />
        </MenuLink>

        <HorizontalFlex className="grow justify">
          <MenuLink href={routes.dashboard}>
            <LogoFI height="3rem" />
          </MenuLink>
          <form className="large-only grow" method="get" action={routes.search}>
            <SearchBar>
              <SearchBarIndicator>
                <FeatherIcon
                  name="search"
                  color={style.black500}
                  alignOnText={false}
                />
              </SearchBarIndicator>
              <SearchBarInput
                ref={inputRef}
                placeholder="Rechercher un groupe ou un évènement"
              />
              <SearchBarButton
                onClick={(e) => {
                  if (inputRef.current.value.trim() === "") {
                    inputRef.current.focus();
                    e.preventDefault();
                  }
                }}
              >
                <FeatherIcon
                  name="arrow-right"
                  color={style.black500}
                  alignOnText={false}
                />
              </SearchBarButton>
            </SearchBar>
          </form>
        </HorizontalFlex>
        <HorizontalFlex>
          <MenuLink href={routes.help} className="large-only">
            <FeatherIcon name="help-circle" />
            <span>Aide</span>
          </MenuLink>
          <ConnectionInfo user={user} routes={routes} />
        </HorizontalFlex>
      </TopBarContainer>
    </TopBarBar>
  );
};
PureTopBar.propTypes = {
  user: PropTypes.shape({
    displayName: PropTypes.string,
    isInsoumise: PropTypes.bool,
  }),
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
};
PureTopBar.defaultProps = {
  user: null,
  routes: {
    dashboard: "#dashboard",
    search: "#search",
    help: "#help",
    personalInformation: "#personalInformation",
    contactConfiguration: "#contactConfiguration",
    signIn: "#signIn",
    logIn: "#logIn",
  },
};

const TopBar = () => {
  const config = useGlobalContext();
  return <PureTopBar {...config} />;
};

export default TopBar;
