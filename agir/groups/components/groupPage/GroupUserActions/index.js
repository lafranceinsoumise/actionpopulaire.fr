import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { mutate } from "swr";

import GroupUserActions from "./GroupUserActions";

import * as api from "@agir/groups/groupPage/api";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

const ConnectedUserActions = (props) => {
  const { id } = props;
  const [isLoading, setIsLoading] = useState(false);
  const user = useSelector(getUser);

  const joinGroup = useCallback(async () => {
    setIsLoading(true);
    let redirectTo = "";
    try {
      const response = await api.joinGroup(id);
      if (response.error) {
        redirectTo = response.error.redirectTo;
      }
    } catch (err) {
      // Reload current page if an unhandled error occurs
      window.location.reload();
    }
    if (redirectTo) {
      window.location = redirectTo;
      return;
    }
    setIsLoading(false);
    mutate(api.getGroupPageEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: true,
      isActiveMember: true,
    }));
  }, [id]);

  const followGroup = useCallback(async () => {
    setIsLoading(true);
    let redirectTo = "";
    try {
      const response = await api.joinGroup(id);
      if (response.error) {
        redirectTo = response.error.redirectTo;
      }
    } catch (err) {
      // Reload current page if an unhandled error occurs
      window.location.reload();
    }
    if (redirectTo) {
      window.location = redirectTo;
      return;
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
