import PropTypes from "prop-types";
import React, { Suspense } from "react";
import { Helmet } from "react-helmet";
import useSWR from "swr";

import { lazy } from "@agir/front/app/utils";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

import GroupsPageHeader from "./GroupsPageHeader";
import GroupCard from "@agir/groups/groupComponents/GroupCard";

import Skeleton from "@agir/front/genericComponents/Skeleton";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";

const UserGroups = lazy(() => import("./UserGroups"));
const GroupSuggestions = lazy(() => import("./GroupSuggestions"));

const GroupsPage = () => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const { data } = useSWR("/api/groupes/");

  return (
    <>
      <Helmet>
        <title>Mes groupes - Action populaire</title>
      </Helmet>
      <GroupsPageHeader />
      <PageFadeIn
        ready={isSessionLoaded && !!data}
        wait={<Skeleton boxes={2} />}
      >
        <Suspense fallback={<Skeleton boxes={2} />}>
          {data ? (
            Array.isArray(data.groups) && data.groups.length > 0 ? (
              <UserGroups groups={data.groups} />
            ) : (
              <GroupSuggestions groups={data?.suggestions} />
            )
          ) : null}
        </Suspense>
      </PageFadeIn>
    </>
  );
};

GroupsPage.propTypes = {
  groupList: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
};

export default GroupsPage;
