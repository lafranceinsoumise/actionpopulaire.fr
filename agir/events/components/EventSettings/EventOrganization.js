import PropTypes from "prop-types";
import React, { useState, useMemo } from "react";
import useSWR, { mutate } from "swr";

import style from "@agir/front/genericComponents/_variables.scss";
import * as api from "@agir/events/common/api";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import SelectField from "@agir/front/formComponents/SelectField";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import MemberList from "./EventMemberList";

import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import Button from "@agir/front/genericComponents/Button";

import { useTransition } from "@react-spring/web";
import { useToast } from "@agir/front/globalContext/hooks.js";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const AddOrganizer = ({ eventPk, participants, onBack }) => {
  const [selectedParticipant, setSelectedParticipant] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const sendToast = useToast();

  const selectParticipant = (value) => {
    setSelectedParticipant(value);
  };

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

const EventOrganization = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event } = useSWR(
    api.getEventEndpoint("getDetailAdvanced", { eventPk })
  );

  const participants = useMemo(() => event?.participants || [], [event]);
  const organizers = useMemo(() => event?.organizers || [], [event]);

  const [submenuOpen, setSubmenuOpen] = useState(false);
  const transition = useTransition(submenuOpen, slideInTransition);

  const openMenu = () => {
    setSubmenuOpen(true);
  };

  const closeMenu = () => {
    setSubmenuOpen(false);
  };

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />

      {event?.groups?.length > 0 && (
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
          <MemberList
            members={event.groups.map((group) => ({ displayName: group.name }))}
          />
          <Spacer size="1rem" />
          <p
            style={{
              margin: 0,
              backgroundColor: style.secondary100,
              color: style.black700,
              padding: "0.75rem 1rem",
              fontSize: "0.875rem",
            }}
          >
            <strong style={{ display: "block", fontWeight: 500 }}>
              Nouvelle version de l'interface de gestion des événements&nbsp;:
            </strong>
            la co-organisation entre les groupes sera de nouveau très vite
            disponible&nbsp;!
          </p>
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
        addButtonLabel="Ajouter un·e autre organisateur·ice"
        onAdd={openMenu}
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
    </>
  );
};
EventOrganization.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventOrganization;
