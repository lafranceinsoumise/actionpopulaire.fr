import PropTypes from "prop-types";
import React from "react";

import Link from "@agir/front/app/Link";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import styled from "styled-components";

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

  @media (min-width: ${(props) => props.theme.collapse}px) {
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

export const ListUser = ({ message, participants }) => {
  if (!message || !participants) {
    return null;
  }

  const totalAnonymous = participants.total - participants.active.length;
  const isOrganizerMessage =
    message.requiredMembershipType > MEMBERSHIP_TYPES.FOLLOWER;

  return (
    <StyledContainer>
      <div>
        {isOrganizerMessage
          ? "Discussion privée avec les animateur·ices du groupe"
          : "Conversation du groupe"}
        &nbsp;
        <Link
          route="groupDetails"
          routeParams={{
            groupPk: message?.group.id,
          }}
          backLink={{
            route: "messages",
            routeParams: { messagePk: message.id },
          }}
        >
          {message.group.name}
        </Link>
      </div>

      <hr />
      <Spacer size="0.5rem" />
      {participants.active.map((user) => (
        <StyledPerson key={user.id}>
          <Avatar image={user.image} name={user.displayName} />
          {user.displayName}
        </StyledPerson>
      ))}
      {totalAnonymous && (
        <StyledBlock>
          <div style={{ width: "1.5rem", marginRight: "0.5rem" }}>
            <RawFeatherIcon name="users" />
          </div>
          {totalAnonymous} autre{totalAnonymous > 1 ? "s" : ""}
        </StyledBlock>
      )}
      <Spacer size="1rem" />
    </StyledContainer>
  );
};
ListUser.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    group: PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
    }),
    author: PropTypes.shape({
      id: PropTypes.string.isRequired,
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired,
    requiredMembershipType: PropTypes.number,
  }).isRequired,
  participants: PropTypes.object,
};

export default ListUser;
