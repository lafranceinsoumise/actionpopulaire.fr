import PropTypes from "prop-types";
import React from "react";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";
import mapImg from "./images/Bloc_map.jpg";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const StyledLink = styled(Link)``;

const StyledMapButton = styled.div`
  max-width: 370px;
  width: 100%;
  overflow: hidden;
  border: 1px solid #ddd;
  border-radius: ${style.borderRadius};
  cursor: pointer;
  margin-bottom: 0.5rem;

  ${StyledLink} > div:first-child {
    height: 80px;
    background-image: url("${mapImg}");
    background-size: cover;
  }
  ${StyledLink} > div:nth-child(2) {
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: ${style.black1000};
  }
`;

const StyledHeaderSearch = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;

  > div:first-child {
    max-width: 480px;
  }
  h1 {
    margin: 0;
  }

  @media (max-width: ${style.collapse}px) {
    flex-direction: column-reverse;
    h1 {
      font-size: 20px;
    }
  }
`;

const SearchBarWrapper = styled.div`
  border-radius: 4px;
  border: 1px solid #dddddd;
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  height: 50px;

  @media (max-width: ${style.collapse}px) {
    height: 40px;
  }
`;

const SearchBarInput = styled.input`
  border: none;
  max-width: 100%;
  width: 90%;
  height: 100%;
  margin-left: 2.5rem;
  padding-left: 0.5rem;
  display: inline-flex;
  flex: 1;

  ::placeholder {
    color: ${style.black500};
    font-weight: 400;
    text-overflow: ellipsis;
    font-size: 0.875rem;
    opacity: 1;
  }
`;

export const MapButton = () => (
  <StyledMapButton>
    <StyledLink route="eventMap">
      <div />
      <div>Voir la carte</div>
    </StyledLink>
  </StyledMapButton>
);

export const HeaderSearch = ({ querySearch, showMap }) => (
  <StyledHeaderSearch>
    <div>
      <h1>
        {!querySearch ? (
          "Rechercher"
        ) : (
          <Hide under>Recherche : "{querySearch}"</Hide>
        )}
      </h1>
      <Hide under as="div" style={{ marginTop: "0.5rem" }}>
        Recherchez des événements et des groupes d'actions par nom, ville, code
        postal...
      </Hide>
    </div>
    {showMap && <MapButton />}
  </StyledHeaderSearch>
);
HeaderSearch.PropTypes = {
  querySearch: PropTypes.string,
  showMap: PropTypes.bool,
};

export const InputSearch = ({
  inputSearch,
  updateSearch,
  placeholder,
  onSubmit,
  isLoading,
}) => (
  <form onSubmit={onSubmit} style={{ display: "flex" }} autoComplete="off">
    <SearchBarWrapper>
      <RawFeatherIcon
        name="search"
        width="1rem"
        height="1rem"
        stroke-width={1.33}
        style={{ position: "absolute", left: "1rem" }}
      />
      <SearchBarInput
        required
        placeholder={placeholder}
        type="text"
        name="q"
        value={inputSearch}
        onChange={updateSearch}
        autoComplete="off"
      />
    </SearchBarWrapper>
    <Hide under>
      <Button
        color="primary"
        onClick={onSubmit}
        style={{ marginLeft: "1rem" }}
        disabled={isLoading}
      >
        Rechercher
      </Button>
    </Hide>
  </form>
);
InputSearch.PropTypes = {
  inputSearch: PropTypes.string,
  updateSearch: PropTypes.func,
  onSubmit: PropTypes.func,
  isLoading: PropTypes.bool,
  placeholder: PropTypes.string,
};
