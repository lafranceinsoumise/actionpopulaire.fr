import PropTypes from "prop-types";
import React, { Fragment } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMemberList from "./GroupMemberList";
import { Hide } from "@agir/front/genericComponents/grid.js";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon.js";
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
          color="primary"
          url={
            Array.isArray(members) &&
            members.map(({ email }) => email).join(", ")
          }
        />
        <Spacer size="1.5rem" />
        <GroupMemberList members={members} />
      </PageFadeIn>
      <Spacer size="2.5rem" />
      {group.routes.membershipTransfer && (
        <a
          href={group?.routes?.membershipTransfer}
          style={{ display: "flex", alignItems: "center" }}
        >
          <RawFeatherIcon name="arrow-right" width="1rem" height="1rem" />
          &ensp;
          <Hide under>
            Transférer des membres de votre{" "}
            {group.is2022 === false ? "groupe" : "équipe"} vers{" "}
            {group.is2022 === false ? "un autre groupe" : "une autre équipe"}
          </Hide>
          <Hide over>
            Transférer des membres vers{" "}
            {group.is2022 === false ? "un autre groupe" : "une autre équipe"}
          </Hide>
        </a>
      )}
    </>
  );
};
GroupMemberPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupMemberPage;
