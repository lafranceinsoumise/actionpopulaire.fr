import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import LogoAP from "@agir/front/genericComponents/LogoAP";

const Lien = styled.a`
  border: none;
  background: none;
  cursor: pointer;

  display: flex;
  align-items: center;
  justify-content: center;

  color: ${({ theme }) => theme.text1000};
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
    color: ${({ theme }) => theme.text1000};

    & > * {
      text-decoration: underline;
    }

    & > div {
      text-decoration: none;
    }
  }

  flex-grow: ${({ grow }) => (grow ? 1 : 0)};
`;

const Container = styled.div`
  width: 100%;
  flex-grow: 0;
  border-bottom: 2px solid ${({ theme }) => theme.text100};
  margin: 0;
  padding: 0;
`;

const Contenu = styled.nav`
  max-width: 1320px;

  background-color: ${(props) => props.theme.background0};
  margin: 0 auto;
  padding: 0 1.5rem;
  @media (max-width: ${({ theme }) => +theme.collapse - 1}px) {
    padding: 0 1rem;
  }

  display: flex;
  justify-content: space-between;
  align:items: center;
`;

const BoutonRetour = ({ onClick }) => {
  const isDesktop = useIsDesktop();

  return (
    <>
      {!isDesktop &&
        (onClick ? (
          <Lien as="button" href="/" aria-label="Retour" onClick={onClick}>
            <FeatherIcon name="arrow-left" />
          </Lien>
        ) : (
          <div style={{ height: "3.5rem", width: "40px" }} />
        ))}
    </>
  );
};
BoutonRetour.propTypes = {
  onClick: PropTypes.func,
};

const BarreSuperieure = ({ onClose }) => {
  const small = useResponsiveMemo(true, false);
  return (
    <Container>
      <Contenu>
        <BoutonRetour onClick={onClose} />
        <Lien href="/" aria-label="Action populaire" grow>
          <LogoAP
            small={small}
            style={{ height: small ? "2.188rem" : "3.5rem", width: "auto" }}
          />
        </Lien>
        <Lien href="https://melenchon2022.fr/le-guide-de-la-recherche-des-parrainages/">
          <FeatherIcon name="help-circle" />
          <span>Aide</span>
        </Lien>
      </Contenu>
    </Container>
  );
};
BarreSuperieure.propTypes = { onClose: PropTypes.func };

export default BarreSuperieure;
