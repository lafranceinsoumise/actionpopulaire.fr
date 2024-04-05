import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";
import { mutate } from "swr";

import EditMembershipDialog from "./EditMembershipDialog";
import FollowGroupDialog from "./FollowGroupDialog";
import GroupUserActions from "./GroupUserActions";
import JoinGroupDialog from "./JoinGroupDialog";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import QuitGroupDialog from "./QuitGroupDialog";
import SecondaryActions from "./SecondaryActions";

import * as api from "@agir/groups/utils/api";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import { routeConfig } from "@agir/front/app/routes.config";
import { useSelectMessage } from "@agir/msgs/common/hooks";
import { useToast } from "@agir/front/globalContext/hooks.js";

import * as style from "@agir/front/genericComponents/_variables.scss";

const StyledContent = styled.div`
  padding: 0;
  display: flex;
  align-items: flex-start;
  flex-flow: column nowrap;
  margin-bottom: 1rem;

  @media (max-width: ${style.collapse}px) {
    background-color: white;
    width: 100%;
    padding: 0 1rem 1.5rem;
    padding-bottom: 0.5rem;
    margin-bottom: 0;
    align-items: center;
    display: ${({ hideOnMobile }) => (hideOnMobile ? "none" : "flex")};
  }
`;

const ConnectedUserActions = (props) => {
  const {
    id,
    name,
    isMember,
    isActiveMember,
    personalInfoConsent,
    contact,
    referents,
    isMessagingEnabled,
  } = props;

  const user = useSelector(getUser);
  const onSelectMessage = useSelectMessage();
  const history = useHistory();
  const sendToast = useToast();

  const [isLoading, setIsLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(null);
  const [joiningStep, setJoiningStep] = useState(0);
  const [messageModalOpen, setMessageModalOpen] = useState(false);
  const [messageErrors, setMessageErrors] = useState(null);

  const closeDialog = useCallback(() => {
    setOpenDialog(null);
  }, []);

  const openJoinDialog = useCallback(() => {
    setOpenDialog("join");
    setJoiningStep(1);
  }, []);

  const closeJoinDialog = useCallback(() => {
    setOpenDialog(null);
    setJoiningStep(0);
  }, []);

  const openEditDialog = useCallback(() => {
    setOpenDialog("edit");
  }, []);

  const openQuitDialog = useCallback(() => {
    setOpenDialog("quit");
  }, []);

  const joinGroup = useCallback(async () => {
    setIsLoading(true);
    const response = await api.joinGroup(id);
    setIsLoading(false);
    if (response?.error?.error_code === "full_group") {
      return history.push(routeConfig.fullGroup.getLink({ groupPk: id }));
    }
    if (response.error) {
      return window.location.reload();
    }
    mutate(api.getGroupEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: true,
      isActiveMember: true,
    }));
    joiningStep > 0 && setJoiningStep(2);
  }, [joiningStep, history, id]);

  const followGroup = useCallback(async () => {
    setIsLoading(true);
    const response = await api.followGroup(id);
    if (response.error) {
      return window.location.reload();
    }
    setIsLoading(false);
    mutate(api.getGroupEndpoint("getGroup", { groupPk: id }), (group) => ({
      ...group,
      isMember: true,
      isActiveMember: false,
    }));
    setOpenDialog("follow");
  }, [id]);

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
        },
      );
      return;
    }
    if (response.error) {
      return window.location.reload();
    }
    setIsLoading(false);
    setOpenDialog(null);
    mutate(api.getGroupEndpoint("getGroup", { groupPk: id }), (group) => ({
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
      },
    );
  }, [id, name, sendToast]);

  const updateOwnMembership = useCallback(
    async (data) => {
      setIsLoading(true);
      const response = await api.updateOwnMembership(id, data);
      if (typeof response.data?.personalInfoConsent !== "undefined") {
        mutate(api.getGroupEndpoint("getGroup", { groupPk: id }), (group) => ({
          ...group,
          personalInfoConsent: response.data.personalInfoConsent,
        }));
      }
      setIsLoading(false);
      joiningStep > 0 ? setJoiningStep(3) : setOpenDialog(null);
    },
    [joiningStep, id],
  );

  const openMessageModal = useCallback(() => {
    closeJoinDialog();
    setMessageModalOpen(true);
  }, [closeJoinDialog]);

  const closeMessageModal = useCallback(() => {
    setMessageModalOpen(false);
    setMessageErrors(null);
  }, []);

  const sendPrivateMessage = useCallback(
    async (message) => {
      setMessageErrors(null);
      const { subject, text, attachment } = message;
      const { data, error } = await api.createPrivateMessage(id, {
        subject,
        text,
        attachment,
      });
      if (error) {
        setMessageErrors(error);
      } else {
        onSelectMessage(data.id);
      }
    },
    [id, onSelectMessage],
  );

  return (
    <>
      <StyledContent>
        <GroupUserActions
          {...props}
          isAuthenticated={!!user}
          isLoading={isLoading}
          onJoin={isMember ? joinGroup : openJoinDialog}
          onFollow={followGroup}
          onEdit={openEditDialog}
          onQuit={openQuitDialog}
        />
        <SecondaryActions {...props} />
      </StyledContent>
      <FollowGroupDialog
        shouldShow={openDialog === "follow"}
        onClose={closeDialog}
        groupName={name}
      />
      <JoinGroupDialog
        id={id}
        step={joiningStep}
        isLoading={isLoading}
        groupName={name}
        groupReferents={referents}
        personName={user.firstName || user.displayName}
        personalInfoConsent={personalInfoConsent}
        onJoin={joinGroup}
        onUpdate={updateOwnMembership}
        onClose={closeJoinDialog}
        openMessageModal={isMessagingEnabled ? openMessageModal : undefined}
        groupContact={contact}
      />
      {isMember && (
        <>
          <EditMembershipDialog
            personalInfoConsent={personalInfoConsent}
            shouldShow={openDialog === "edit"}
            isLoading={isLoading}
            onUpdate={updateOwnMembership}
            onClose={closeDialog}
          />
          <QuitGroupDialog
            groupName={name}
            shouldShow={openDialog === "quit"}
            isActiveMember={isActiveMember}
            isLoading={isLoading}
            onClose={closeDialog}
            onQuit={quitGroup}
          />
          {isMessagingEnabled && (
            <MessageModal
              shouldShow={messageModalOpen}
              user={user}
              groupPk={id}
              onSend={sendPrivateMessage}
              onClose={closeMessageModal}
              errors={messageErrors}
              onBoarding
            />
          )}
        </>
      )}
    </>
  );
};

ConnectedUserActions.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  contact: PropTypes.object,
  isMember: PropTypes.bool,
  isActiveMember: PropTypes.bool,
  referents: PropTypes.array,
  personalInfoConsent: PropTypes.bool,
  isMessagingEnabled: PropTypes.bool,
};

export default ConnectedUserActions;
