import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import { useMiniSearch } from "@agir/lib/utils/search";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import ThematicGroupCard from "./ThematicGroupCard";
import CounterBadge from "@agir/front/app/Navigation/CounterBadge";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledList = styled.ul`
  margin: 0;
  padding: 0;
  list-style: none;
  scroll-margin-top: 72px;

  & > *:not(:first-child) {
    margin-top: 1rem;
  }

  & > h4 {
    margin: 0;
    padding: 0;
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1.5;
    min-height: 4rem;
    display: flex;
    align-items: center;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.375rem;
    }
  }
`;
const StyledContainer = styled.div`
  margin: 0;
  padding: 0;
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;

  & > nav {
    ul {
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-flow: column nowrap;

      li {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
        font-weight: 700;
        line-height: 1.5;
        box-shadow: 0px -1px 0px 0px #dfdfdf inset;

        &:last-child {
          box-shadow: none;
        }

        ${Button} {
          text-align: left;
          line-height: 1.2;
        }

        ${CounterBadge} {
          flex: 0 0 auto;
        }
      }
    }
  }
`;

const ThematicGroupList = (props) => {
  const { groups } = props;

  const parsedGroups = useMemo(() => {
    if (!Array.isArray(groups) || groups.length === 0) {
      return [];
    }
    return groups
      .filter((group) => !!group.subtype)
      .map((group) => ({
        ...group,
      }));
  }, [groups]);

  const [searchTerm, setSearchTerm, visibleGroups] = useMiniSearch(
    parsedGroups,
    {
      fields: ["name", "description"],
      searchOptions: { boost: { name: 2 } },
    },
  );

  const handleSearch = useCallback(
    (e) => {
      setSearchTerm(e.target.value);
    },
    [setSearchTerm],
  );

  return (
    <StyledContainer>
      {parsedGroups.length > 0 && (
        <TextField
          id="search"
          name="search"
          value={searchTerm}
          onChange={handleSearch}
          placeholder="Rechercher un groupe"
          aria-label="Rechercher un groupe"
          icon="magnifying-glass:solid"
          label=""
          dark
        />
      )}
      <Spacer size="1rem" />
      {visibleGroups.length === 0 && (
        <p>
          <em>— Aucun groupe thématique n'a été retrouvé !</em>
        </p>
      )}
      <StyledList>
        {visibleGroups.map((group) => (
          <li key={group.id}>
            <ThematicGroupCard {...group} />
          </li>
        ))}
      </StyledList>
    </StyledContainer>
  );
};

ThematicGroupList.propTypes = {
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    }),
  ),
};

export default ThematicGroupList;
