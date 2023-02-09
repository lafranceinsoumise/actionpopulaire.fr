import PropTypes from "prop-types";
import React, { useState, useMemo } from "react";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";
import * as api from "@agir/events/common/api";

import Spacer from "@agir/front/genericComponents/Spacer.js";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import MemberList from "./EventMemberList";
import GroupList from "./GroupList";
import GroupItem from "./GroupItem";
import AddOrganizer from "./Organization/AddOrganizer";
import AddGroupOrganizer from "./Organization/AddGroupOrganizer";

import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";
import { useTransition } from "@react-spring/web";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const MENU_ORGANIZER = "menu-organizer";
const MENU_GROUP = "menu-group";

const EventOrganization = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event } = useSWR(
    api.getEventEndpoint("getDetailAdvanced", { eventPk })
  );

  const participants = useMemo(
    () => event?.participants?.filter((p) => !p.isOrganizer) || [],
    [event]
  );
  const organizers = useMemo(
    () => event?.participants?.filter((p) => p.isOrganizer) || [],
    [event]
  );
  const groups = useMemo(() => event?.groups || [], [event]);
  const groupsInvited = useMemo(() => event?.groupsInvited || [], [event]);

  const [submenuOpen, setSubmenuOpen] = useState(null);

  const transition = useTransition(!!submenuOpen, slideInTransition);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />

      <StyledTitle>Groupes organisateurs</StyledTitle>
      <span style={{ color: style.black700 }}>
        Les groupes organisateurs de l'événement.
      </span>
      <Spacer size=".5rem" />
      <span style={{ color: style.black700 }}>
        Tous les animateur·ices de ces groupes peuvent accéder à la gestion de
        l'événement et la liste des participant·es.
      </span>
      <Spacer size="1rem" />

      <GroupList
        groups={groups}
        addButtonLabel={
          event && !event.isPast ? "Ajouter un groupe co-organisateur" : ""
        }
        onAdd={
          event && !event.isPast ? () => setSubmenuOpen(MENU_GROUP) : undefined
        }
      >
        {groupsInvited?.map((group) => (
          <GroupItem
            key={group.id}
            id={group.id}
            name={group.name}
            image={group.image}
            label="Invitation en attente"
            disabled
          />
        ))}
      </GroupList>
      <Spacer size="1.5rem" />

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
        onAdd={
          event && !event.isPast
            ? () => setSubmenuOpen(MENU_ORGANIZER)
            : undefined
        }
      />

      <Spacer size="1rem" />

      {transition(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              {MENU_ORGANIZER === submenuOpen && (
                <AddOrganizer
                  onClick={() => setSubmenuOpen(false)}
                  eventPk={eventPk}
                  participants={participants}
                  onBack={() => setSubmenuOpen(null)}
                />
              )}
              {MENU_GROUP === submenuOpen && (
                <AddGroupOrganizer
                  onClick={() => setSubmenuGroupOpen(false)}
                  eventPk={eventPk}
                  groups={groups}
                  onBack={() => setSubmenuOpen(null)}
                />
              )}
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
