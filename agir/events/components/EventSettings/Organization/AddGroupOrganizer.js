import PropTypes from "prop-types";
import React, { useState } from "react";
import { mutate } from "swr";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import * as api from "@agir/events/common/api";
import * as apiGroup from "@agir/groups/api";

import Spacer from "@agir/front/genericComponents/Spacer.js";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import GroupList from "../GroupList";
import GroupItem from "../GroupItem";

import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { useToast } from "@agir/front/globalContext/hooks.js";

const StyledListBlock = styled.div`
  div {
    display: inline-flex;
    width: 0.5rem;
    height: 0.5rem;
    background-color: ${style.primary500};
    border-radius: 2rem;
    margin-right: 0.5rem;
  }
`;

const StyledSearch = styled.div`
  border-radius: ${style.borderRadius};
  border: 1px solid #ddd;
  display: flex;
  height: 2.5rem;

  > input {
    width: 90%;
    height: 100%;
    border: none;
  }

  ${RawFeatherIcon} {
    padding-left: 1rem;
    padding-right: 1rem;
  }
`;

export const AddGroupOrganizer = ({ eventPk, groups, onBack }) => {
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [groupSearched, setGroupSearched] = useState([]);
  const [search, setSearch] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
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
    sendToast("Invitation envoyée", "SUCCESS", { autoClose: true });
    mutate(api.getEventEndpoint("getDetailAdvanced", { eventPk }));
    onBack();
  };

  const handleSearch = async (searchTerm) => {
    const { data, errors } = await apiGroup.searchGroups(searchTerm);
    // Filter already organizer groups
    setGroupSearched(
      data.results.filter(
        (result) => !groups.some((group) => group.id === result.id)
      )
    );
  };

  const handleChange = (e) => {
    setSearch(e.target.value);
    if (e.target.value.length >= 3) {
      handleSearch(e.target.value);
      return;
    }
    setGroupSearched([]);
  };

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
          <span style={{ color: style.black700 }}>
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

          {!!groupSearched?.length && (
            <>
              <Spacer size="2rem" />
              {groupSearched.slice(0, 20).length > 20 && (
                <p>20 des {groupSearched.length} résultats</p>
              )}
              <GroupList
                groups={groupSearched.slice(0, 20)}
                selectGroup={setSelectedGroup}
              />
              <Spacer size="1rem" />
            </>
          )}

          {search.length < 3 && (
            <p>
              <Spacer size="1rem" />
              Ecrivez au moins 3 caractères
            </p>
          )}

          {search.length >= 3 && !groupSearched?.length && (
            <p>
              <Spacer size="1rem" />
              {isLoading
                ? "Recherche en cours"
                : "Aucun groupe ne correspond à cette recherche"}
            </p>
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
