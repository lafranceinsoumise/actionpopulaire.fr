import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useHistory } from "react-router-dom";
import { mutate } from "swr";

import GroupUserActions from "./GroupUserActions";
import QuitGroupDialog from "./QuitGroupDialog";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import * as api from "@agir/groups/groupPage/api";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import { routeConfig } from "@agir/front/app/routes.config";
import { useToast } from "@agir/front/globalContext/hooks.js";

const modalJoinDescription = (
  <>
    Vous venez de rejoindre le groupe en tant que membre. Les animateur·ices du
    groupe ont été informé·es de votre arrivée.
    <Spacer size="0.5rem" />
    C’est maintenant que tout se joue : faites la rencontre avec les
    animateur·ices.
    <Spacer size="0.5rem" />
    Envoyez-leur un message pour vous présenter&nbsp;!
  </>
);
const modalJoinConfirm = (
  <>
    <RawFeatherIcon name="mail" width="1.2rem" />
    &nbsp; Je me présente !
  </>
);
const modalJoinDismiss = "Non merci";
const modalFollowDescription = (
  <>
    Vous recevrez l’actualité de ce groupe.
    <Spacer size="0.5rem" />
    Vous pouvez le rejoindre en tant que membre pour recevoir les messages
    destinés aux membres actifs à tout moment.
  </>
);

const ConnectedUserActions = (props) => {
  const { id, name, isMember, isActiveMember } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [isQuitting, setIsQuitting] = useState(false);

  const [isOpenModalJoin, setIsOpenModalJoin] = useState(false);
  const [isOpenModalFollow, setIsOpenModalFollow] = useState(false);

  const modalJoinTitle = <>Bienvenue dans le groupe {name} ! 👋</>;
  const modalFollowTitle = <>Vous suivez {name} ! 👋</>;

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
    setIsOpenModalJoin(true);
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
    setIsOpenModalFollow(true);
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

      <ModalConfirmation
        key={1}
        shouldShow={isOpenModalJoin}
        onClose={() => setIsOpenModalJoin(false)}
        title={modalJoinTitle}
        description={modalJoinDescription}
        dismissLabel={modalJoinDismiss}
        confirmationLabel={modalJoinConfirm}
        confirmationUrl="messages"
      />
      <ModalConfirmation
        key={2}
        shouldShow={isOpenModalFollow}
        onClose={() => setIsOpenModalFollow(false)}
        title={modalFollowTitle}
        description={modalFollowDescription}
      />
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
