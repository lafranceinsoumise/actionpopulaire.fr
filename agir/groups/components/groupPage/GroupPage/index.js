import PropTypes from "prop-types";
import React, { useEffect } from "react";

import GroupPageComponent from "./GroupPage";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { setIs2022 } from "@agir/front/globalContext/actions";
import {
  getIsSessionLoaded,
  getIsConnected,
  getBackLink,
} from "@agir/front/globalContext/reducers";

import { useGroupDetail } from "./hooks";

const GroupPage = (props) => {
  const { groupPk, activeTab } = props;

  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const isConnected = useSelector(getIsConnected);
  const backLink = useSelector(getBackLink);
  const dispatch = useDispatch();

  const {
    group,
    groupSuggestions,
    upcomingEvents,
    pastEvents,
    loadMorePastEvents,
    isLoadingPastEvents,
    pastEventReports,
  } = useGroupDetail(groupPk);

  const { is2022 } = group || {};

  useEffect(() => {
    is2022 === true && dispatch(setIs2022());
  }, [is2022, dispatch]);

  return (
    <GroupPageComponent
      backLink={backLink}
      isConnected={isSessionLoaded && isConnected}
      isLoading={!isSessionLoaded || !group}
      group={group}
      upcomingEvents={upcomingEvents}
      pastEvents={pastEvents}
      isLoadingPastEvents={isLoadingPastEvents}
      loadMorePastEvents={loadMorePastEvents}
      pastEventReports={pastEventReports}
      groupSuggestions={Array.isArray(groupSuggestions) ? groupSuggestions : []}
      activeTab={activeTab}
    />
  );
};
GroupPage.propTypes = {
  groupPk: PropTypes.string,
  activeTab: PropTypes.string,
};
export default GroupPage;
