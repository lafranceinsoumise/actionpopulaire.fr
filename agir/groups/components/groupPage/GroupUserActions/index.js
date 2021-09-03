import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useHistory } from "react-router-dom";
import { mutate } from "swr";

import GroupUserActions from "./GroupUserActions";
import QuitGroupDialog from "./QuitGroupDialog";

import * as api from "@agir/groups/groupPage/api";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import { routeConfig } from "@agir/front/app/routes.config";
import { useToast } from "@agir/front/globalContext/hooks.js";

const ConnectedUserActions = (props) => {
  const { id, name, isMember, isActiveMember } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [isQuitting, setIsQuitting] = useState(false);

  const user = useSelector(getUser);
  const history = useHistory();
  const sendToast = useToast();

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
    sendToast(
      <>
        Vous êtes maintenant membre du groupe <strong>{name}</strong>&nbsp;!
      </>,
      "SUCCESS",
      {
        autoClose: true,
      }
    );
    mutate(api.getGroupPageEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: true,
      isActiveMember: true,
    }));
  }, [history, sendToast, id, name]);

  const followGroup = useCallback(async () => {
    setIsLoading(true);
    const response = await api.followGroup(id);
    if (response.error) {
      return window.location.reload();
    }
    setIsLoading(false);
    sendToast(
      <>
        Vous êtes maintenant abonné·e au groupe <strong>{name}</strong>&nbsp;!
      </>,
      "SUCCESS",
      {
        autoClose: true,
      }
    );
    mutate(api.getGroupPageEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: true,
      isActiveMember: false,
    }));
  }, [id, name, sendToast]);

  const quitGroup = useCallback(async () => {
    setIsLoading(true);
    const response = await api.quitGroup(id);
    if (response?.error?.error_code === "group_last_referent") {
      sendToast(
        <>
          Désolé, vous ne pouvez pas quitter le groupe <strong>{name}</strong>,
          car vous en êtes l'animateur·ice.
        </>,
        "ERROR",
        {
          autoClose: true,
        }
      );
      return;
    }
    if (response.error) {
      return window.location.reload();
    }
    setIsLoading(false);
    setIsQuitting(false);
    mutate(api.getGroupPageEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: false,
      isActiveMember: false,
    }));
    sendToast(
      <>
        Vous avez quitté le groupe <strong>{name}</strong>.
      </>,
      "SUCCESS",
      {
        autoClose: true,
      }
    );
  }, [id, name, sendToast]);

  const openQuitDialog = useCallback(() => {
    setIsQuitting(true);
  }, []);

  const closeQuitDialog = useCallback(() => {
    setIsQuitting(false);
  }, []);

  return (
    <>
      <GroupUserActions
        {...props}
        isAuthenticated={!!user}
        isLoading={isLoading}
        onJoin={joinGroup}
        onFollow={followGroup}
        onQuit={openQuitDialog}
      />
      {isMember && (
        <QuitGroupDialog
          groupName={name}
          shouldShow={isQuitting}
          isActiveMember={isActiveMember}
          isLoading={isLoading}
          onDismiss={isLoading ? undefined : closeQuitDialog}
          onConfirm={quitGroup}
        />
      )}
    </>
  );
};

ConnectedUserActions.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  isMember: PropTypes.bool,
  isActiveMember: PropTypes.bool,
  routes: PropTypes.shape({
    quit: PropTypes.string,
  }),
};

export default ConnectedUserActions;
