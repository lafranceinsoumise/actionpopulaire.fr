import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";
import * as api from "@agir/events/common/api";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import SelectField from "@agir/front/formComponents/SelectField";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import MemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

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
    const res = await api.addOrganizer(eventPk, selectedParticipant);
    setIsLoading(false);
    if (res.error) {
      console.log("error", res.error);
      sendToast(res.error, "ERROR", { autoClose: true });
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });

    onBack();
  };

  return (
    <>
      <BackButton onClick={onBack} />
      <StyledTitle>Ajouter un autre organisateur</StyledTitle>
      <Spacer size="1rem" />

      {!participants?.length ? (
        <span style={{ color: style.black700 }}>
          Accueillez d’abord un·e participant·e à l'événement pour pouvoir lui
          donner un rôle d'organisateur·ice.
        </span>
      ) : (
        <SelectField
          label="Choisir un participant"
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
        </>
      )}

      <Spacer size="1rem" />
      <Button color="secondary" onClick={onSubmit} disabled={isLoading}>
        Confirmer
      </Button>
    </>
  );
};

const EventOrganization = (props) => {
  const { onBack, illustration, eventPk } = props;

  // const group = {
  //   email: "pole@group.com",
  //   displayName: "Pôle groupe d'action",
  // };

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getParticipants", { eventPk })
  );

  const [submenuOpen, setSubmenuOpen] = useState(false);
  const transition = useTransition(submenuOpen, slideInTransition);

  const handleBack = useCallback(() => {
    setSubmenuOpen(false);
  }, []);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />

      {/* <StyledTitle>Groupes co-organisateurs</StyledTitle>

      <Spacer size="1rem" />
      <span style={{ color: style.black700 }}>
        Invitez des groupes à organiser votre événement.Ils s’afficheront sur la
        page publiquement.
      </span>

      <Spacer size="1rem" />
      <MemberList
        members={[group]}
        addButtonLabel="Ajouter un groupe co-organisateur"
        onAdd={() => {
          console.log("Add group right !");
        }}
        isLoading={isLoading}
      />

      <Spacer size="2rem" /> */}

      <StyledTitle>Participants organisateurs</StyledTitle>

      <Spacer size="1rem" />
      <span style={{ color: style.black700 }}>
        Donnez des droits d’accès à des participant·es pour leur permettre de
        gérer l’événement.
      </span>

      <Spacer size="1rem" />
      <MemberList
        members={event?.organizers}
        addButtonLabel="Ajouter un autre organisateur"
        onAdd={() => setSubmenuOpen(true)}
      />

      <Spacer size="1rem" />

      {transition(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              <AddOrganizer
                onClick={(e) => {
                  setSubmenuOpen(false);
                }}
                eventPk={eventPk}
                // Participants not organizers
                participants={
                  event?.participants?.filter(
                    (x) =>
                      !!event?.organizers?.filter((y) => x.id !== y.id)?.length
                  ) || []
                }
                onBack={handleBack}
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
