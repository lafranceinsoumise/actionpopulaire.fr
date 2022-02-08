import PropTypes from "prop-types";
import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import Avatar from "@agir/front/genericComponents/Avatar";
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { routeConfig } from "@agir/front/app/routes.config";

const StyledPerson = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;

  ${Avatar} {
    width: 2rem;
    height: 2rem;
    margin-right: 0.5rem;
  }
`;

const StyledContainer = styled.div`
  padding: 1rem;

  @media (min-width: ${style.collapse}px) {
    max-width: 400px;
    padding: 0;
  }
`;

const StyledBlock = styled.div`
  display: flex;
  padding-left: 0.25rem;
  align-items: center;

  ${RawFeatherIcon} {
    padding-right: 0.5rem;
    color: #777777;
  }
`;

const HiddenUsers = ({ total }) => {
  if (!total) {
    return null;
  }
  return (
    <StyledBlock>
      <div style={{ width: "1.5rem", marginRight: "0.5rem" }}>
        <RawFeatherIcon name="users" />
      </div>
      {total} autre{total > 1 ? "s" : ""}
    </StyledBlock>
  );
};

export const ListUser = ({ message, participants }) => {
  if (!message || !participants) {
    return null;
  }

  const totalAnonymous = participants.total - participants.active.length;
  const isOrganizerMessage =
    message.requiredMembershipType > MEMBERSHIP_TYPES.FOLLOWER;
  const groupURL = routeConfig.groupDetails.getLink({
    groupPk: message?.group.id,
  });

  return (
    <StyledContainer>
      <div>
        {isOrganizerMessage
          ? "Discussion privée avec les animateur·ices du groupe"
          : "Conversation du groupe"}
        &nbsp;
        <Link to={groupURL}>{message.group.name}</Link>
      </div>

      <hr />
      <Spacer size="0.5rem" />
      {participants.active.map((user) => (
        <StyledPerson key={user.id}>
          <Avatar image={user.image} name={user.displayName} />
          {user.displayName}
        </StyledPerson>
      ))}

      <HiddenUsers total={totalAnonymous} />
      <Spacer size="1rem" />
    </StyledContainer>
  );
};
ListUser.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    group: PropTypes.shape({
      name: PropTypes.string,
    }),
    author: PropTypes.shape({
      id: PropTypes.string.isRequired,
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired,
  }).isRequired,
  participants: PropTypes.object,
};

export default ListUser;
