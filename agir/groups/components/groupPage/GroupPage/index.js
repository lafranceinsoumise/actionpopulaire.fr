import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import useSWR, { useSWRInfinite } from "swr";
import GroupPageComponent from "./GroupPage";

import logger from "@agir/lib/utils/logger";

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

const log = logger(__filename);

const GroupPage = (props) => {
  const { groupPk } = props;
  const { data: group } = useSWR(`/api/groupes/${groupPk}`);
  log.debug("Group data", group);
  const { data: groupSuggestions } = useSWR(
    `/api/groupes/${groupPk}/suggestions`
  );
  log.debug("Group suggestions", groupSuggestions);
  const { data: upcomingEvents } = useSWR(
    `/api/groupes/${groupPk}/evenements/a-venir`
  );
  log.debug("Group upcoming events", upcomingEvents);
  const { data: pastEventData, size, setSize, isValidating } = useSWRInfinite(
    (pageIndex) =>
      `/api/groupes/${groupPk}/evenements/passes?page=${
        pageIndex + 1
      }&page_size=3`
  );
  const pastEvents = useMemo(() => {
    let events = [];
    if (!Array.isArray(pastEventData)) {
      return events;
    }
    pastEventData.forEach(({ results }) => {
      if (Array.isArray(results)) {
        events = events.concat(results);
      }
    });
    return events;
  }, [pastEventData]);
  log.debug("Group past events", pastEvents);
  const pastEventCount = useMemo(() => {
    if (!Array.isArray(pastEventData) || !pastEventData[0]) {
      return 0;
    }
    return pastEventData[0].count;
  }, [pastEventData]);
  const loadMorePastEvents = useCallback(() => {
    setSize(size + 1);
  }, [setSize, size]);
  const isLoadingPastEvents = !pastEventData || isValidating;

  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const isConnected = useSelector(getIsConnected);
  const backLink = useSelector(getBackLink);
  const dispatch = useDispatch();

  const { is2022 } = group || {};

  React.useEffect(() => {
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
      loadMorePastEvents={
        pastEventCount > pastEvents.length ? loadMorePastEvents : undefined
      }
      groupSuggestions={Array.isArray(groupSuggestions) ? groupSuggestions : []}
    />
  );
};
GroupPage.propTypes = {
  groupPk: PropTypes.string,
};
export default GroupPage;
