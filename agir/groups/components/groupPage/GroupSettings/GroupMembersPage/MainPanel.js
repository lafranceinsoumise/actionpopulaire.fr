import PropTypes from "prop-types";
import React, { Fragment, useMemo } from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

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
      <Spacer size="2.5rem" />
      <StyledTitle>
        {followers.length}&nbsp;
        {followers.length === 1 ? "Abonné·e" : "Abonné·es"}
      </StyledTitle>
      <p style={{ color: style.black700, margin: 0 }}>
        Toutes les personnes intéressées par votre groupe. Vous pouvez passer un
        membre actif en abonné·e.
      </p>
      <Spacer size="1rem" />
      {followers.length > 0 ? (
        <>
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
      ) : (
        <p
          style={{
            padding: "1.5rem",
            boxShadow: style.cardShadow,
            borderRadius: style.borderRadius,
          }}
        >
          Votre groupe n'a pas encore d'abonné·es.
          <br />
          <br />
          <strong style={{ fontWeight: 600 }}>
            Vous pouvez passer un membre qui n'est plus actif sur le groupe en
            abonné
          </strong>
          , pour qu'il ne compte pas dans votre nombre de membres actifs. Il ne
          recevra plus certains messages destinés aux membres actifs.
          <br />
          <br />
          N'importe quel membre d'Action Populaire peut suivre votre groupe en
          cliquant sur le bouton "Suivre" sur la page de votre groupe.
          <br />
          <br />
          Il n'y a pas de limite de nombre d'abonné·es&nbsp;:{" "}
          <strong style={{ fontWeight: 600 }}>
            essayez d'en avoir le plus possible&nbsp;!
          </strong>
        </p>
      )}
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
