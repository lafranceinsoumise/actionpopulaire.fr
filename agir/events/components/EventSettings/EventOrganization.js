import PropTypes from "prop-types";
import React, { useState, useMemo, useCallback } from "react";
import useSWR, { mutate } from "swr";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import * as api from "@agir/events/common/api";
import * as apiGroup from "@agir/groups/groupPage/api";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import SelectField from "@agir/front/formComponents/SelectField";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import MemberList from "./EventMemberList";
import GroupList from "./GroupList";
import GroupItem from "./GroupItem";

import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useTransition } from "@react-spring/web";
import { useToast } from "@agir/front/globalContext/hooks.js";

const StyledList = styled.div`
  display: flex;
  align-items: center;
  div {
    display: inline-flex;
    width: 0.5rem;
    height: 0.5rem;
    background-color: ${style.primary500};
    border-radius: 2rem;
    margin-right: 0.5rem;
  }
`;

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

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const AddOrganizer = ({ eventPk, participants, onBack }) => {
  const [selectedParticipant, setSelectedParticipant] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const sendToast = useToast();

  const selectParticipant = (value) => setSelectedParticipant(value);

  const onSubmit = async () => {
    setIsLoading(true);
    const res = await api.addOrganizer(eventPk, {
      organizer_id: selectedParticipant.value.id,
    });
    setIsLoading(false);
    if (res.errors) {
      sendToast(res.errors.detail, "ERROR", { autoClose: true });
      onBack();
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    mutate(api.getEventEndpoint("getDetailAdvanced", { eventPk }));
    onBack();
  };

  return (
    <>
      <BackButton onClick={onBack} />
      <StyledTitle>Ajouter un·e autre organisateur·ice</StyledTitle>
      <Spacer size="1rem" />

      {!participants.length ? (
        <span style={{ color: style.black700 }}>
          Accueillez d’abord un·e participant·e à l'événement pour pouvoir lui
          donner un rôle d'organisateur·ice.
        </span>
      ) : (
        <SelectField
          label="Choisir un·e participant·e"
          placeholder="Sélection"
          options={participants.map((participant) => ({
            label: `${participant.displayName} (${participant.email})`,
            value: participant,
          }))}
          onChange={selectParticipant}
          value={selectedParticipant}
        />
      )}

      {selectedParticipant && (
        <>
          <Spacer size="1rem" />
          <MemberList members={[selectedParticipant.value]} />
          <Spacer size="1rem" />
          <div>
            Ce participant pourra :
            <Spacer size="0.5rem" />
            <StyledList>
              <div />
              Voir la liste des participant·es
            </StyledList>
            <StyledList>
              <div />
              Modifier les organisateurs
            </StyledList>
            <StyledList>
              <div />
              Modifier les informations de l’événement
            </StyledList>
            <StyledList>
              <div />
              Annuler l’événement
            </StyledList>
          </div>
          <Spacer size="1rem" />
          <Button color="secondary" onClick={onSubmit} disabled={isLoading}>
            Confirmer
          </Button>
        </>
      )}
    </>
  );
};
AddOrganizer.propTypes = {
  onBack: PropTypes.func,
  participants: PropTypes.arrayOf(PropTypes.object),
  eventPk: PropTypes.string,
};

const AddGroupOrganizer = ({ eventPk, groups, onBack }) => {
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
    // if (res.errors) {
    //   sendToast(res.errors.detail, "ERROR", { autoClose: true });
    //   onBack();
    //   return;
    // }
    // sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    // mutate(api.getEventEndpoint("getDetailAdvanced", { eventPk }));
    // onBack();
  };

  const selectGroup = useCallback((value) => {
    setSelectedGroup(value);
  }, []);

  const handleChange = (e) => {
    setSearch(e.target.value);
    if (e.target.value.length >= 3) {
      handleSearch(e.target.value);
      return;
    }
    setGroupSearched([]);
  };

  const handleSearch = async (e) => {
    const { data, errors } = await apiGroup.searchGroup(e);
    // Filter already organizer groups
    setGroupSearched(
      data.results.reduce((result, groupSearch) => {
        if (!groups.some((group) => group.id === groupSearch.id)) {
          return [...result, groupSearch];
        }
        return result;
      }, [])
    );
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
              {groupSearched.slice(0, 4).length > 4 && (
                <p>4 des {groupSearched.length} résultats</p>
              )}
              <GroupList
                groups={groupSearched.slice(0, 4)}
                selectGroup={selectGroup}
              />
              <Spacer size="1rem" />
            </>
          )}

          {search.length >= 3 && !groupSearched?.length && (
            <>
              <Spacer size="2rem" />
              <p>Aucun groupe ne correspond à cette recherche</p>
            </>
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
              <b>Si ses gestionnaires acceptent la co-organisation</b>, ce
              groupe s’affichera sur la page publique de l’événement
            </StyledListBlock>
            <StyledListBlock>
              <div />
              Ces derniers <b>ne pourront pas accéder aux paramètres</b> de
              l’événement sauf si vous leur en donnez les droits.
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

const EventOrganization = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event } = useSWR(
    api.getEventEndpoint("getDetailAdvanced", { eventPk })
  );

  const participants = useMemo(() => event?.participants || [], [event]);
  const organizers = useMemo(() => event?.organizers || [], [event]);
  const groups = useMemo(() => event?.groups || [], [event]);

  const [submenuOpen, setSubmenuOpen] = useState(false);
  const [submenuGroupOpen, setSubmenuGroupOpen] = useState(false);

  const transition = useTransition(submenuOpen, slideInTransition);
  const transitionGroup = useTransition(submenuGroupOpen, slideInTransition);

  const openMenu = () => setSubmenuOpen(true);
  const closeMenu = () => setSubmenuOpen(false);

  const openMenuGroup = () => setSubmenuGroupOpen(true);
  const closeMenuGroup = () => setSubmenuGroupOpen(false);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />

      {!!event?.groups?.length && (
        <>
          <StyledTitle>Groupes</StyledTitle>
          <span style={{ color: style.black700 }}>
            Les groupes organisateurs de l'événement.
          </span>
          <Spacer size=".5rem" />
          <span style={{ color: style.black700 }}>
            Tous les animateur·ices de ces groupes peuvent accéder à la gestion
            de l'événement et la liste des participant·es.
          </span>
          <Spacer size="1rem" />

          <GroupList
            groups={groups}
            addButtonLabel={
              event && !event.isPast ? "Ajouter un groupe co-organisateur" : ""
            }
            onAdd={event && !event.isPast ? openMenuGroup : undefined}
          />
          <Spacer size="1.5rem" />
        </>
      )}

      <StyledTitle>Participant·es organisateur·ices</StyledTitle>
      <span style={{ color: style.black700 }}>
        Donnez des droits d’accès à des participant·es pour leur permettre de
        gérer l’événement.
      </span>
      <Spacer size="1.5rem" />
      <MemberList
        members={organizers}
        addButtonLabel={
          event && !event.isPast ? "Ajouter un·e autre organisateur·ice" : ""
        }
        onAdd={event && !event.isPast ? openMenu : undefined}
      />

      <Spacer size="1rem" />

      {transition(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              <AddOrganizer
                onClick={() => setSubmenuOpen(false)}
                eventPk={eventPk}
                participants={participants}
                onBack={closeMenu}
              />
            </PanelWrapper>
          )
      )}

      {transitionGroup(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              <AddGroupOrganizer
                onClick={() => setSubmenuGroupOpen(false)}
                eventPk={eventPk}
                groups={groups}
                onBack={closeMenuGroup}
              />
            </PanelWrapper>
          )
      )}
    </>
  );
};
EventOrganization.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventOrganization;
