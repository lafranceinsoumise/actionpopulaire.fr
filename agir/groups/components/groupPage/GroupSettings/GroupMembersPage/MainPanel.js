import PropTypes from "prop-types";
import React, { useMemo } from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

const GroupMemberMainPanel = (props) => {
  const { routes, members, onClickMember } = props;

  const activeMembers = useMemo(() => {
    if (!Array.isArray(members)) {
      return [];
    }
    return members.filter(
      (member) => member.membershipType >= MEMBERSHIP_TYPES.MEMBER
    );
  }, [members]);

  const emails = useMemo(
    () =>
      activeMembers
        .filter(
          ({ hasGroupNotifications, email }) => email && hasGroupNotifications
        )
        .map(({ email }) => email)
        .join(", "),
    [activeMembers]
  );

  return (
    <>
      <StyledTitle>
        {activeMembers.length}&nbsp;
        {activeMembers.length > 1 ? "Membres actifs" : "Membre actif"}
      </StyledTitle>
      <p style={{ color: style.black700, margin: 0 }}>
        Vos membres impliqués activement. Quand une personne rejoint votre
        groupe, elle est considérée comme membre actif.
      </p>
      <Spacer size="1rem" />
      <ShareLink
        label="Copier les e-mails des membres"
        color="primary"
        url={emails}
        $wrap
      />
      <Spacer size="1.5rem" />
      <GroupMemberList members={activeMembers} onClickMember={onClickMember} />
      <Spacer size="2.5rem" />
      {routes?.membershipTransfer && (
        <a
          href={routes.membershipTransfer}
          style={{ display: "flex", alignItems: "flex-start" }}
        >
          <RawFeatherIcon
            name="arrow-right"
            width="1rem"
            height="1rem"
            style={{ paddingTop: "3px" }}
          />
          <Spacer size="0.5rem" />
          Transférer des membres vers un autre groupe
        </a>
      )}
    </>
  );
};
GroupMemberMainPanel.propTypes = {
  routes: PropTypes.object,
  members: PropTypes.arrayOf(PropTypes.object),
  onClickMember: PropTypes.func,
};
export default GroupMemberMainPanel;
