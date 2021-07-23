import PropTypes from "prop-types";
import React, { useState } from "react";
import useSWR from "swr";
import * as api from "@agir/events/common/api";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Spacer from "@agir/front/genericComponents/Spacer.js";

import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

const EventRights = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );

  const [isLoading, setIsLoading] = useState(false);

  const group = {
    email: "pole@group.com",
    displayName: "Pôle groupe d'action",
  };
  const members = [
    { email: "pascal@preprod.com", displayName: "Pascal Preprod" },
  ];

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Droits sur l’événement</StyledTitle>

      <span style={{ color: style.black700 }}>
        Donnez des droits d’accès à des participant·es pour leur permettre de
        gérer l’événement.
      </span>

      <Spacer size="1rem" />

      <GroupMemberList
        members={members}
        addButtonLabel="Ajouter un autre organisateur"
        onAdd={() => {
          console.log("AJOUT D'UN ORGA !");
        }}
        isLoading={isLoading}
      />

      <Spacer size="1rem" />
    </>
  );
};
EventRights.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventRights;
