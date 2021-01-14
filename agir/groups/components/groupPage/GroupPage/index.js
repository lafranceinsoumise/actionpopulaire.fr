import PropTypes from "prop-types";
import React from "react";
import useSWR from "swr";
import GroupPageComponent from "./GroupPage";

import logger from "@agir/lib/utils/logger";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { setIs2022 } from "@agir/front/globalContext/actions";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

const log = logger(__filename);

const GroupPage = (props) => {
  const { groupPk } = props;
  const { data: group } = useSWR(`/api/groupes/${groupPk}`);
  const { data: groupSuggestions } = useSWR(
    `/api/groupes/${groupPk}/suggestions`
  );
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  const dispatch = useDispatch();

  log.debug("Group data", group);
  log.debug("Group suggestions", groupSuggestions);

  const { is2022 } = group || {};

  React.useEffect(() => {
    is2022 === true && dispatch(setIs2022());
  }, [is2022, dispatch]);

  return (
    <GroupPageComponent
      isLoading={!isSessionLoaded || !group}
      group={group}
      groupSuggestions={Array.isArray(groupSuggestions) ? groupSuggestions : []}
    />
  );
};
GroupPage.propTypes = {
  groupPk: PropTypes.string,
};
export default GroupPage;
