import React, { Fragment, useState, useEffect } from "react";
import Link from "@agir/front/app/Link";
import GroupMember from "./GroupMember";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import GroupInvitation from "./GroupInvitation";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";

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

  const [members, setMembers] = useState([]);

  const getMembersAPI = async (groupPk) => {
    const { data } = await getMembers(groupPk);
    setMembers(data);
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
        url={members.map(({ email }) => email).join(", ")}
      />

      <Spacer size="2rem" />

      {members.map((member) => (
        <Fragment key={member?.id}>
          <GroupMember
            name={member?.displayName}
            email={member?.email}
            image={member?.image}
            membershipType={member?.membershipType}
            assets={member?.assets}
          />
          <Spacer size="1rem" />
        </Fragment>
      ))}
      <Spacer size="2rem" />

      <ShareLink
        label="Copier"
        url={`https://actionpopulaire.fr/groupe/${group?.id}`}
        title={`Partagez le lien public ${
          group.is2022 ? "de l'équipe" : "du groupe"
        }`}
      />

      {/* {group.is2022 === false && (
        <>
          <Spacer size="2rem" />
          <GroupInvitation
            groupPk={groupPk}
            title={
              <>
                Invitez de nouveaux membres{" "}
                <InlineBlock>dans votre groupe !</InlineBlock>
              </>
            }
          />
        </>
      )} */}

      <hr />

      <Link href={group?.routes?.membershipTransfer}>
        {`Transférer des membres de votre ${
          group.is2022 === false ? "groupe" : "équipe"
        } vers ${
          group.is2022 === false ? "un autre groupe" : "une autre équipe"
        }`}
      </Link>
    </>
  );
};

export default GroupMemberPage;
