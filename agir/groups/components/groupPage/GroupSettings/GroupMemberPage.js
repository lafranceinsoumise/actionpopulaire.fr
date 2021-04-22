import React, { useEffect } from "react";
import Link from "@agir/front/app/Link";
import GroupMember from "./GroupMember";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import GroupInvitation from "./GroupInvitation";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";

import { DEFAULT_EMAILS, DEFAULT_MEMBERS } from "./group_items.js";
import { StyledTitle } from "./styledComponents.js";
import styled from "styled-components";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";
import { getMembers } from "@agir/groups/groupPage/api.js";

const InlineBlock = styled.div`
  display: inline-block;
`;

const GroupMemberPage = (props) => {
  const { onBack, illustration, groupPk } = props;

  const group = useGroup(groupPk);

  const getMembersAPI = async (groupPk) => {
    const res = await getMembers(groupPk);
    console.log("get members from group : ", res);
  };

  useEffect(() => {
    getMembersAPI(groupPk);
  }, [groupPk]);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>{group?.facts?.memberCount} Membres</StyledTitle>

      <ShareLink
        label="Copier les mails des membres"
        color="secondary"
        url={DEFAULT_EMAILS.join(", ")}
      />

      <Spacer size="2rem" />

      {DEFAULT_MEMBERS.map((e, id) => (
        <>
          <GroupMember
            key={id}
            name={e.name}
            role={e.role}
            email={e.email}
            assets={e.assets}
          />
          <Spacer size="1rem" />
        </>
      ))}

      <Spacer size="2rem" />

      <ShareLink
        label="Copier"
        url={`https://actionpopulaire.fr/groupe/${group?.id}`}
        title="Partagez le lien public de l'équipe"
      />

      <Spacer size="2rem" />
      <GroupInvitation
        title={
          <>
            Invitez de nouveaux membres{" "}
            <InlineBlock>dans votre équipe !</InlineBlock>
          </>
        }
      />

      <hr />

      <Link href={group?.routes?.membershipTransfer}>
        Transférer des membres de votre équipe vers une autre équipe
      </Link>
    </>
  );
};

export default GroupMemberPage;
