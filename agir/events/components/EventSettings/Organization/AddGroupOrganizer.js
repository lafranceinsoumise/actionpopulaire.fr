import _debounce from "lodash/debounce";
import PropTypes from "prop-types";
import React, { useEffect, useMemo, useState } from "react";
import styled from "styled-components";
import { mutate } from "swr";

import * as api from "@agir/events/common/api";
import * as apiGroup from "@agir/groups/utils/api";
import { useToast } from "@agir/front/globalContext/hooks.js";

import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import Button from "@agir/front/genericComponents/Button";
import GroupList from "../GroupList";
import GroupItem from "../GroupItem";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";

const StyledListBlock = styled.div`
  div {
    display: inline-flex;
    width: 0.5rem;
    height: 0.5rem;
    background-color: ${(props) => props.theme.primary500};
    border-radius: 2rem;
    margin-right: 0.5rem;
  }
`;

const StyledSearch = styled.div`
  border-radius: ${(props) => props.theme.borderRadius};
  border: 1px solid #ddd;
  display: flex;
  height: 2.5rem;

  & > input {
    width: 90%;
    height: 100%;
    border: none;
  }

  ${RawFeatherIcon} {
    padding-left: 1rem;
    padding-right: 1rem;
  }
`;

const START_SEARCH = 3;
const MAX_RESULTS = 20;

export const AddGroupOrganizer = ({ eventPk, groups, onBack }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState([]);
  const [groupSuggestions, setGroupSuggestions] = useState([]);
  const [groupSearchResults, setGroupSearchResults] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);

  const sendToast = useToast();

  const onSubmit = async () => {
    setIsLoading(true);

    const res = await api.inviteGroupOrganizer(eventPk, {
      groupPk: selectedGroup.id,
    });

    setIsLoading(false);
    if (res.errors) {
      sendToast(res.errors.detail, "ERROR", { autoClose: true });
      onBack();
      return;
    }
    if (res.data.created) {
      sendToast(
        "Le groupe, dont vous êtes animateur·ice, a été ajouté à l'organisation de l'événement",
        "SUCCESS",
        { autoClose: true },
      );
    } else {
      sendToast(
        "Une invitation a été envoyée aux animateur·ices du groupe",
        "SUCCESS",
        { autoClose: true },
      );
    }
    mutate(api.getEventEndpoint("getDetailAdvanced", { eventPk }));
    onBack();
  };

  const handleSearch = useMemo(
    () =>
      _debounce(async (searchTerm) => {
        const { data } = await apiGroup.searchGroups(searchTerm);
        // Filter already organizer groups
        setGroupSearchResults(
          data.results
            .filter((result) => !groups.some((group) => group.id === result.id))
            .slice(0, MAX_RESULTS),
        );
        setIsLoading(false);
      }, 300),
    [groups],
  );

  const handleChange = (e) => {
    setSearch(e.target.value);
    setGroupSearchResults([]);
    if (e.target.value.length >= START_SEARCH) {
      setIsLoading(true);
      handleSearch(e.target.value);
    }
  };

  useEffect(() => {
    (async () => {
      const { data } = await api.getOrganizerGroupSuggestions(eventPk);
      const suggestions = Array.isArray(data) ? data : [];
      setGroupSuggestions(suggestions);
    })();
  }, [eventPk]);

  return (
    <>
      <BackButton onClick={onBack} />
      <StyledTitle>
        {!selectedGroup
          ? "Co-organisation"
          : "Ajouter un groupe en co-organisation"}
      </StyledTitle>
      <Spacer size="1rem" />

      {!selectedGroup ? (
        <>
          <span
            css={`
              color: ${(props) => props.theme.text700};
            `}
          >
            Invitez des groupes à organiser votre événement. Ils s’afficheront
            sur la page publiquement.
          </span>

          <Spacer size="1rem" />

          <StyledSearch>
            <RawFeatherIcon name="search" width="1rem" height="1rem" />
            <input
              type="text"
              value={search}
              onChange={handleChange}
              placeholder="Chercher un groupe..."
            />
          </StyledSearch>
          <Spacer size="1rem" />
          <div>
            {search.length < START_SEARCH ? (
              <span>Ecrivez au moins {START_SEARCH} caractères</span>
            ) : isLoading ? (
              <span>Recherche en cours...</span>
            ) : groupSearchResults.length === 0 ? (
              <span>Aucun groupe ne correspond à cette recherche</span>
            ) : (
              <h4>Résultats</h4>
            )}
            {groupSearchResults.length > 0 && (
              <GroupList
                groups={groupSearchResults}
                selectGroup={setSelectedGroup}
              />
            )}
          </div>
          <Spacer size="1rem" />
          {groupSuggestions.length > 0 && (
            <div>
              <h4>Derniers groupes co-organisateurs</h4>
              <GroupList
                groups={groupSuggestions}
                selectGroup={setSelectedGroup}
              />
            </div>
          )}
        </>
      ) : (
        <>
          <GroupList>
            <GroupItem key={selectedGroup.id} {...selectedGroup} />
          </GroupList>
          <Spacer size="1rem" />
          <div>
            <StyledListBlock>
              <div />
              <b>Si ses animateur·ices acceptent la co-organisation</b>, ce
              groupe s’affichera sur la page publique de l’événement
            </StyledListBlock>
            <Spacer size="0.5rem" />
            <StyledListBlock>
              <div />
              Ces dernier·es <b>pourront accéder aux paramètres</b> de
              l’événement.
            </StyledListBlock>
          </div>
          <Spacer size="1rem" />
          <Button color="secondary" onClick={onSubmit} disabled={isLoading}>
            Envoyer l'invitation
          </Button>
        </>
      )}
    </>
  );
};
AddGroupOrganizer.propTypes = {
  onBack: PropTypes.func,
  groups: PropTypes.arrayOf(PropTypes.object),
  eventPk: PropTypes.string,
};

export default AddGroupOrganizer;
