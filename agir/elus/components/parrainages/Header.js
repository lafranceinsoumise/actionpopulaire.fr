import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import LogoAP from "@agir/front/genericComponents/LogoAP";

const HeaderLink = styled.a`
  border: none;
  background: none;
  cursor: pointer;

  display: flex;
  align-items: center;
  justify-content: center;

  color: ${({ theme }) => theme.black1000};
  font-weight: 500;
  height: 4.5rem;
  padding: 0 0.5rem;
  @media (max-width: ${({ theme }) => theme.collapse}px) {
    height: 3.5rem;
  }

  * + * {
    margin-left: 0.5em;
  }

  :hover {
    outline: none;
    text-decoration: none;
    color: ${({ theme }) => theme.black1000};

    & > * {
      text-decoration: underline;
    }

    & > div {
      text-decoration: none;
    }
  }

  flex-grow: ${({ grow }) => (grow ? 1 : 0)};
`;

const HeaderContainer = styled.div`
  width: 100%;
  flex-grow: 0;
  border-bottom: 2px solid ${({ theme }) => theme.black100};
  margin: 0;
  padding: 0;
`;

const HeaderContent = styled.nav`
  max-width: 1320px;

  background-color: #fff;
  margin: 0 auto;
  padding: 0 1.5rem;
  @media (max-width: ${({ theme }) => +theme.collapse - 1}px) {
    padding: 0 1rem;
  }

  display: flex;
  justify-content: space-between;
  align:items: center;
`;

const BackButton = ({ onClick }) => {
  const isDesktop = useIsDesktop();

  return (
    <>
      {!isDesktop &&
        (onClick ? (
          <HeaderLink
            as="button"
            href="/"
            aria-label="Retour"
            onClick={onClick}
          >
            <FeatherIcon name="arrow-left" />
          </HeaderLink>
        ) : (
          <div style={{ height: "3.5rem", width: "40px" }} />
        ))}
    </>
  );
};
BackButton.propTypes = {
  onClick: PropTypes.func,
};

const Header = ({ onClose }) => {
  const small = useResponsiveMemo(true, false);
  return (
    <HeaderContainer>
      <HeaderContent>
        <BackButton onClick={onClose} />
        <HeaderLink href="/" aria-label="Action populaire" grow>
          <LogoAP
            small={small}
            style={{ height: small ? "2.188rem" : "3.5rem", width: "auto" }}
          />
        </HeaderLink>
        <HeaderLink href="https://melenchon2022.fr/le-guide-de-la-recherche-des-parrainages/">
          <FeatherIcon name="help-circle" />
          <span>Aide</span>
        </HeaderLink>
      </HeaderContent>
    </HeaderContainer>
  );
};
Header.propTypes = { onClose: PropTypes.func };

export default Header;
