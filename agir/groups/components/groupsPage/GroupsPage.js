import PropTypes from "prop-types";
import React, { Suspense } from "react";
import useSWR from "swr";

import { lazy } from "@agir/front/app/utils";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

import GroupsPageHeader from "./GroupsPageHeader";
import GroupCard from "@agir/groups/groupComponents/GroupCard";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const StyledContainer = styled.div`
  padding-bottom: 64px;

  @media (max-width: ${style.collapse}px) {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
`;

const UserGroups = lazy(() => import("./UserGroups"));
const GroupSuggestions = lazy(() => import("./GroupSuggestions"));

const GroupsPage = () => {
  const user = useSelector(getUser);
  const hasOwnGroups = Array.isArray(user?.groups) && user.groups.length > 0;
  const { data: userGroups } = useSWR(
    !!user && hasOwnGroups && "/api/groupes/",
  );
  const { data: groupSuggestions } = useSWR(
    !!user && !hasOwnGroups && "/api/groupes/suggestions/",
  );
  const isReady = !!user && (userGroups || groupSuggestions);

  return (
    <>
      <GroupsPageHeader />
      <PageFadeIn ready={isReady} wait={<Skeleton boxes={2} />}>
        <Suspense fallback={<Skeleton boxes={2} />}>
          <StyledContainer>
            {isReady && userGroups && <UserGroups groups={userGroups} />}
            {isReady && groupSuggestions && (
              <GroupSuggestions groups={groupSuggestions} />
            )}
          </StyledContainer>
        </Suspense>
      </PageFadeIn>
    </>
  );
};

GroupsPage.propTypes = {
  groupList: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
};

export default GroupsPage;
