import PropTypes from "prop-types";
import React, { useMemo } from "react";

import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

const GroupMemberMainPanel = (props) => {
  const { members, onClickMember } = props;

  const emails = useMemo(
    () =>
      members
        .filter(
          ({ hasGroupNotifications, email }) => email && hasGroupNotifications,
        )
        .map(({ email }) => email)
        .join(", "),
    [members],
  );

  return (
    <>
      <StyledTitle>
        {members.length}&nbsp;
        {members.length > 1 ? "Membres" : "Membre"}
      </StyledTitle>
      <p style={{ color: style.text700, margin: 0 }}>
        Retrouvez ici la liste des membres de votre groupe
      </p>
      <Spacer size="1rem" />
      <ShareLink
        label="Copier les e-mails des membres"
        color="primary"
        url={emails}
        $wrap
      />
      <Spacer size="1.5rem" />
      <GroupMemberList
        sortable
        searchable
        members={members}
        onClickMember={onClickMember}
      />
    </>
  );
};
GroupMemberMainPanel.propTypes = {
  routes: PropTypes.object,
  members: PropTypes.arrayOf(PropTypes.object),
  group: PropTypes.object,
};
export default GroupMemberMainPanel;
