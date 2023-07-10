import PropTypes from "prop-types";
import React, { Fragment, useMemo } from "react";

import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

import Button from "@agir/front/genericComponents/Button";
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
      <StyledTitle
        css={`
          display: flex;
          align-items: center;
        `}
      >
        {`${followers.length || ""} Contact${
          followers.length === 1 ? "" : "s"
        }`.trim()}
      </StyledTitle>
      <p
        css={`
          color: ${({ theme }) => theme.black700};
          margin: 0;
        `}
      >
        Toutes les personnes intéressées par votre groupe.
      </p>
      {emails ? (
        <>
          <Spacer size="1rem" />
          <ShareLink
            label="Copier les e-mails"
            color="primary"
            url={emails}
            $wrap
          />
        </>
      ) : null}
      {followers.length > 0 ? (
        <>
          <Spacer size="1.5rem" />
          <GroupMemberList
            searchable
            sortable
            members={followers}
            onClickMember={onClickMember}
          />
        </>
      ) : (
        <>
          <Spacer size="1.5rem" />
          <p>
            Vous n’avez pas encore de contact !
            <Spacer size="0.5rem" />
            Obtenez des contacts pour partager les actions de votre groupe
            d’action et du mouvement.
          </p>
          <Spacer size=".5rem" />
          <Button link icon="user-plus" route="createContact" color="secondary">
            Ajouter un contact
          </Button>
        </>
      )}
      <Spacer size="2rem" />
      <footer
        css={`
          color: ${({ theme }) => theme.black700};
          font-size: 0.875rem;
        `}
      >
        <p>
          Lorsque vous ajoutez un contact, ou bien quand un membre d’Action
          Populaire clique sur “Suivre le groupe”, ses informations s’affichent
          ici.
        </p>
        <p>
          Vos contacts qui reçoivent vos messages et nouveaux événements par
          e-mail sont indiqués comme « abonnés ».
        </p>
        <p>Les contacts ne comptent pas dans le total des membres du groupe.</p>
      </footer>
    </>
  );
};
GroupContactsMainPanel.propTypes = {
  members: PropTypes.arrayOf(PropTypes.object),
  onClickMember: PropTypes.func,
};
export default GroupContactsMainPanel;
