import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useHistory } from "react-router-dom";
import { mutate } from "swr";

import GroupUserActions from "./GroupUserActions";

import * as api from "@agir/groups/groupPage/api";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import { routeConfig } from "@agir/front/app/routes.config";

const ConnectedUserActions = (props) => {
  const { id } = props;
  const [isLoading, setIsLoading] = useState(false);
  const user = useSelector(getUser);
  const history = useHistory();

  const joinGroup = useCallback(async () => {
    setIsLoading(true);
    const response = await api.joinGroup(id);
    if (response?.error?.error_code === "full_group") {
      return history.push(routeConfig.fullGroup.getLink({ groupPk: id }));
    }
    if (response.error) {
      return window.location.reload();
    }
    setIsLoading(false);
    mutate(api.getGroupPageEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: true,
      isActiveMember: true,
    }));
  }, [history, id]);

  const followGroup = useCallback(async () => {
    setIsLoading(true);
    const response = await api.followGroup(id);
    if (response.error) {
      return window.location.reload();
    }
    setIsLoading(false);
    mutate(api.getGroupPageEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: true,
      isActiveMember: false,
    }));
  }, [id]);

  const quitGroup = useCallback(() => {
    if (props.routes?.quit) {
      window.location = props.routes.quit;
    }
  }, [props.routes]);

  return (
    <GroupUserActions
      {...props}
      isAuthenticated={!!user}
      isLoading={isLoading}
      onJoin={joinGroup}
      onFollow={followGroup}
      onQuit={quitGroup}
    />
  );
};

ConnectedUserActions.propTypes = {
  id: PropTypes.string.isRequired,
  routes: PropTypes.shape({
    quit: PropTypes.string,
  }),
};

export default ConnectedUserActions;
