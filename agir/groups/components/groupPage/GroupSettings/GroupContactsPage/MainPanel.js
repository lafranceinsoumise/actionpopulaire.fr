import PropTypes from "prop-types";
import React, { Fragment, useMemo } from "react";

import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

const GroupContactsMainPanel = (props) => {
  const { members, onClickMember } = props;

  const followers = useMemo(() => {
    if (!Array.isArray(members)) {
      return [];
    }
    return members.filter(
      (member) => member.membershipType <= MEMBERSHIP_TYPES.FOLLOWER
    );
  }, [members]);

  const emails = useMemo(
    () =>
      followers
        .filter(
          ({ hasGroupNotifications, email }) => hasGroupNotifications && email
        )
        .map(({ email }) => email)
        .join(", "),
    [followers]
  );

  return (
    <>
      <StyledTitle>
        {followers.length}&nbsp; Contact{followers.length > 1 ? "s" : ""}
      </StyledTitle>
      <p
        css={`
          color: ${({ theme }) => theme.black700};
          margin: 0;
        `}
      >
        Toutes les personnes intéressées par votre groupe.
      </p>
      <Spacer size="1rem" />
      <ShareLink
        label="Copier les e-mails"
        color="primary"
        url={emails}
        $wrap
      />
      <Spacer size="1.5rem" />
      <GroupMemberList members={followers} onClickMember={onClickMember} />
      <Spacer size="2rem" />
      <p
        css={`
          color: ${({ theme }) => theme.black700};
          font-size: 0.875rem;
        `}
      >
        Lorsque vous ajoutez un contact, ou bien quand un membre d’Action
        Populaire clique sur “Suivre le groupe”, ses informations s’affichent
        ici.
      </p>
      <p
        css={`
          color: ${({ theme }) => theme.black700};
          font-size: 0.875rem;
        `}
      >
        Les contacts ne comptent pas dans le total des membres du groupe.
      </p>
    </>
  );
};
GroupContactsMainPanel.propTypes = {
  members: PropTypes.arrayOf(PropTypes.object),
  onClickMember: PropTypes.func,
};
export default GroupContactsMainPanel;
