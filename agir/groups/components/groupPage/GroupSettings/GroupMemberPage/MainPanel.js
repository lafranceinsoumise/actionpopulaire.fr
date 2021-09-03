import PropTypes from "prop-types";
import React, { Fragment, useMemo } from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/groups/groupPage/GroupSettings/styledComponents";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

const GroupMemberMainPanel = (props) => {
  const { routes, members, onChangeMembershipType } = props;

  const [activeMembers, followers] = useMemo(() => {
    if (!Array.isArray(members)) {
      return [[], []];
    }
    const activeMembers = [];
    const followers = [];
    members.forEach((member) => {
      member.membershipType <= MEMBERSHIP_TYPES.FOLLOWER
        ? followers.push(member)
        : activeMembers.push(member);
    });
    return [activeMembers, followers];
  }, [members]);

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
        url={activeMembers.map(({ email }) => email).join(", ")}
        $wrap
      />
      <Spacer size="1.5rem" />
      <GroupMemberList
        members={activeMembers}
        onChangeMembershipType={onChangeMembershipType}
      />
      {followers.length > 0 ? (
        <>
          <Spacer size="2.5rem" />
          <StyledTitle>
            {followers.length}&nbsp;
            {followers.length > 1 ? "Abonné·es" : "Abonné·e"}
          </StyledTitle>
          <p style={{ color: style.black700, margin: 0 }}>
            Toutes les personnes intéressées par votre groupe. Vous pouvez
            passer un membre actif en abonné·e.
          </p>
          <Spacer size="1rem" />
          <ShareLink
            label="Copier les e-mails des abonné·es"
            color="primary"
            url={followers.map(({ email }) => email).join(", ")}
            $wrap
          />
          <Spacer size="1.5rem" />
          <GroupMemberList
            members={followers}
            onChangeMembershipType={onChangeMembershipType}
          />
        </>
      ) : null}
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
  onChangeMembershipType: PropTypes.func,
};
export default GroupMemberMainPanel;
