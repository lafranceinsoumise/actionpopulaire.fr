import PropTypes from "prop-types";
import React, { Fragment } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";
import GroupMember from "./GroupMember";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn.js";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";
import { getGroupPageEndpoint } from "@agir/groups/groupPage/api.js";

const StyledSkeleton = styled.div`
  & > * {
    background-color: ${style.black50};
    margin: 0;
    width: 100%;
  }

  & > :first-child {
    height: 37px;
    margin: 0.5rem 0;
  }

  & > :nth-child(2) {
    height: 56px;
    margin-bottom: 2rem;
  }

  & > :last-child {
    height: 177px;
  }
`;

const MembersSkeleton = (
  <StyledSkeleton>
    <div />
    <div />
    <div />
  </StyledSkeleton>
);

const GroupMemberPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const group = useGroup(groupPk);
  const { data: members } = useSWR(
    getGroupPageEndpoint("getMembers", { groupPk })
  );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <PageFadeIn ready={Array.isArray(members)} wait={MembersSkeleton}>
        <StyledTitle>{group?.facts?.memberCount} Membres</StyledTitle>
        <ShareLink
          label="Copier les mails des membres"
          color="secondary"
          url={
            Array.isArray(members) &&
            members.map(({ email }) => email).join(", ")
          }
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
      </PageFadeIn>
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
GroupMemberPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupMemberPage;
