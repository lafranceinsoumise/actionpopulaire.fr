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

const StyledBlock = styled.div`
  display: flex;
  padding-left: 0.25rem;
  align-items: center;
`;

const HiddenUsers = ({ total }) => {
  if (!total) {
    return null;
  }
  return (
    <StyledBlock>
      <RawFeatherIcon name="users" style={{ paddingRight: "0.5rem" }} />
      {total} autre{total > 1 ? "s" : ""}
    </StyledBlock>
  );
};

const UsersRole = ({ users, role, authors }) => {
  if (!users.length) {
    return null;
  }

  // Show anonymous for each role
  // let totalAnonymous = 0;
  // if (Array.isArray(authors)) {
  //   totalAnonymous = users.reduce((total, user) => total + (authors.includes(user.id)) , 0);
  // }

  return (
    <>
      <span style={{ fontWeight: 500 }}>{role}</span>
      <Spacer size="0.5rem" />
      {users.map((user) => (
        <StyledPerson>
          <Avatar image={user.image} name={user.displayName} />
          {user.displayName}
        </StyledPerson>
      ))}
      {/* <HiddenUsers total={totalAnonymous} /> */}
      <Spacer size="1rem" />
    </>
  );
};

export const ListUser = ({ message }) => {
  if (!message) {
    return null;
  }

  const participants = message.participants;
  const author = participants.actives.filter((p) => !!p.isAuthor);
  const commentAuthors = participants.commentAuthors;
  const totalAnonymous = participants.total - participants.actives.length;

  const isOrganizerMessage =
    message.requiredMembershipType > MEMBERSHIP_TYPES.FOLLOWER;
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
        <UsersRole
          role="Gestionnaires"
          users={managers}
          authors={commentAuthors}
        />
        <UsersRole
          role="Membres actifs"
          users={members}
          authors={commentAuthors}
        />
        <UsersRole role="Contacts" users={followers} authors={commentAuthors} />

        {!!totalAnonymous && (
          <>
            <hr style={{ marginTop: 0 }} />
            <HiddenUsers total={totalAnonymous} />
          </>
        )}
      </div>
    </StyledContainer>
  );
};

export default ListUser;
