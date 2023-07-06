import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import { Hide } from "@agir/front/genericComponents/grid";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import SelectField from "@agir/front/formComponents/SelectField";
import Spacer from "@agir/front/genericComponents/Spacer";

import mapImg from "./images/Bloc_map.jpg";

import { OPTIONS } from "./config.js";

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

export const SearchTooShort = ({ search }) => {
  if (!search || search?.length >= 3) {
    return null;
  }
  return (
    <>
      <Spacer size="1rem" />
      Rentrez au moins 3 caractères pour effectuer une recherche
    </>
  );
};
SearchTooShort.propTypes = {
  search: PropTypes.string,
};

export const HeaderSearch = ({ querySearch, mapRoute }) => (
  <StyledHeaderSearch>
    <div>
      <h1>
        <Hide $over>Rechercher</Hide>
        {!querySearch && <Hide $under>Recherche : "{querySearch}"</Hide>}
      </h1>
      <Hide $under as="div" style={{ marginTop: "0.5rem" }}>
        Recherchez des événements et des groupes d'actions par nom, ville, code
        postal...
      </Hide>
    </div>
    {!!mapRoute && (
      <StyledMapButton>
        <StyledLink route={mapRoute}>
          <div />
          <div>Voir la carte</div>
        </StyledLink>
      </StyledMapButton>
    )}
  </StyledHeaderSearch>
);
HeaderSearch.propTypes = {
  querySearch: PropTypes.string,
  mapRoute: PropTypes.oneOf(["eventMap", "groupMap"]),
};

export const InputSearch = ({ inputSearch, updateSearch, placeholder }) => (
  <div style={{ display: "flex" }}>
    <SearchBarWrapper>
      <RawFeatherIcon
        name="search"
        width="1rem"
        height="1rem"
        strokeWidth={1.33}
        style={{ position: "absolute", left: "1rem" }}
      />
      <SearchBarInput
        required
        placeholder={placeholder}
        type="text"
        name="q"
        onChange={updateSearch}
        autoComplete="off"
        maxLength="512"
        value={inputSearch.slice(0, 512)}
      />
    </SearchBarWrapper>
  </div>
);
InputSearch.propTypes = {
  inputSearch: PropTypes.string,
  updateSearch: PropTypes.func,
  placeholder: PropTypes.string,
};

export const EventFilters = ({ filters, setFilter }) => {
  return (
    <>
      <SelectField
        label="Trier par"
        placeholder="Trier par..."
        name="eventSort"
        value={filters?.eventSort}
        onChange={(value) => setFilter("eventSort", value)}
        options={OPTIONS.EventSort}
      />
      <SelectField
        label="Catégorie d'événement"
        placeholder="Categories"
        name="eventSchedule"
        value={filters?.eventSchedule}
        onChange={(value) => setFilter("eventSchedule", value)}
        options={OPTIONS.EventCategory}
      />
      <SelectField
        label="Type"
        placeholder="Types"
        name="eventType"
        value={filters?.eventType}
        onChange={(value) => setFilter("eventType", value)}
        options={OPTIONS.EventType}
      />
    </>
  );
};
EventFilters.propTypes = {
  filters: PropTypes.object,
  setFilter: PropTypes.func,
};

export const GroupFilters = ({ filters, setFilter }) => {
  return (
    <>
      <SelectField
        label="Trier par"
        placeholder="Trier par..."
        name="groupSort"
        value={filters?.groupSort}
        onChange={(value) => setFilter("groupSort", value)}
        options={OPTIONS.GroupSort}
      />
      <SelectField
        label="Type"
        placeholder="Types"
        name="groupType"
        value={filters?.groupType}
        onChange={(value) => setFilter("groupType", value)}
        options={OPTIONS.GroupType}
      />
      <div
        css={`
          display: flex;
          align-items: flex-end;
          padding: 10px 0;
        `}
      >
        <CheckboxField
          label="Uniquement les groupes les plus actifs"
          name="groupInactive"
          value={!filters?.groupInactive}
          onChange={({ target }) =>
            setFilter(
              "groupInactive",
              target.checked ? undefined : { value: "1" }
            )
          }
        />
      </div>
    </>
  );
};
GroupFilters.propTypes = EventFilters.propTypes;

export const FilterButton = ({ showFilters, switchFilters }) => (
  <>
    <Spacer size="1rem" />
    <div style={{ textAlign: "right" }}>
      <Button
        small
        icon={!showFilters ? "filter" : "x-circle"}
        onClick={switchFilters}
      >
        {!showFilters ? "Filtrer" : "Supprimer les filtres"}
      </Button>
    </div>
  </>
);
FilterButton.propTypes = {
  showFilters: PropTypes.bool,
  switchFilters: PropTypes.func,
};
