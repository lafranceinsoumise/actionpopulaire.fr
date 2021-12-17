import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import Avatar from "@agir/front/genericComponents/Avatar";
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

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
    width: 400px;
    background-color: #fafafa;
    padding: 1.5rem;
    border-left: 1px solid #c4c4c4;
  }
`;

const UsersRole = ({ users, role }) => {
  if (!users.length) {
    return null;
  }

  return (
    <>
      <span style={{ fontWeight: "500" }}>{role}</span>
      <Spacer size="0.5rem" />
      {users.map((user) => (
        <StyledPerson>
          <Avatar image={user.image} name={user.displayName} />
          {user.displayName}
        </StyledPerson>
      ))}
      <Spacer size="1rem" />
    </>
  );
};

export const ListUser = (props) => {
  const { message } = props;

  if (!message) {
    return null;
  }

  const isOrganizerMessage =
    message.requiredMembershipType > MEMBERSHIP_TYPES.MEMBER;
  const totalAnonymous =
    message.participants.total - message.participants.actives.length;

  const referents = message.participants.actives.filter(
    (p) => p.membershipType === MEMBERSHIP_TYPES.REFERENT
  );
  const managers = message.participants.actives.filter(
    (p) => p.membershipType === MEMBERSHIP_TYPES.MANAGER
  );
  const members = message.participants.actives.filter(
    (p) => p.membershipType === MEMBERSHIP_TYPES.MEMBER
  );
  const followers = message.participants.actives.filter(
    (p) => p.membershipType === MEMBERSHIP_TYPES.FOLLOWER
  );

  const author = message.participants.actives.filter((p) => !!p.isAuthor);

  return (
    <StyledContainer>
      <div style={{ color: style.primary500 }}>
        <RawFeatherIcon name="users" />
        <Spacer size="0.25rem" />
        {isOrganizerMessage
          ? "Discussion privée avec les animateur·ices du groupe"
          : "Conversation du groupe"}
      </div>

      <Spacer size="0.25rem" />
      {message.group.name}

      <hr />

      <div>
        {author[0].membershipType === 0 && (
          <UsersRole role="Non membre" users={author} />
        )}
        <UsersRole role="Animateurs" users={referents} />
        <UsersRole role="Gestionnaires" users={managers} />
        <UsersRole role="Membres actifs" users={members} />
        <UsersRole role="Contacts" users={followers} />
      </div>

      {!!totalAnonymous && (
        <div
          style={{
            display: "flex",
            paddingLeft: "0.25rem",
            alignItems: "center",
          }}
        >
          <RawFeatherIcon name="users" style={{ paddingRight: "0.5rem" }} />
          {totalAnonymous} autres
        </div>
      )}
    </StyledContainer>
  );
};

export default ListUser;
