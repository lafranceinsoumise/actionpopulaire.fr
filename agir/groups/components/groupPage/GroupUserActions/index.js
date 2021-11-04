import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useHistory } from "react-router-dom";
import { mutate } from "swr";

import GroupUserActions from "./GroupUserActions";
import SecondaryActions from "./SecondaryActions";
import FollowGroupDialog from "./FollowGroupDialog";
import JoinGroupDialog from "./JoinGroupDialog";
import EditMembershipDialog from "./EditMembershipDialog";
import QuitGroupDialog from "./QuitGroupDialog";

import * as api from "@agir/groups/api";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import { routeConfig } from "@agir/front/app/routes.config";
import { useToast } from "@agir/front/globalContext/hooks.js";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

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
  } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(null);
  const [joiningStep, setJoiningStep] = useState(0);

  const user = useSelector(getUser);
  const history = useHistory();
  const sendToast = useToast();

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
    if (response?.error?.error_code === "full_group") {
      return history.push(routeConfig.fullGroup.getLink({ groupPk: id }));
    }
    if (response.error) {
      return window.location.reload();
    }
    setIsLoading(false);
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
        }
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
      }
    );
  }, [id, name, sendToast]);

  const updateOwnMembership = useCallback(
    async (data) => {
      setIsLoading(true);
      const response = await api.updateOwnMembership(id, data);
      if (typeof response.personalInfoConsent !== "undefined") {
        mutate(api.getGroupEndpoint("getGroup", { groupPk: id }), (group) => ({
          ...group,
          personalInfoConsent: response.personalInfoConsent,
        }));
      }
      setIsLoading(false);
      joiningStep > 0 ? setJoiningStep(3) : setOpenDialog(null);
    },
    [joiningStep, history, id]
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
        step={joiningStep}
        isLoading={isLoading}
        groupName={name}
        groupContact={contact}
        groupReferents={referents}
        personName={user.firstName || user.displayName}
        onJoin={joinGroup}
        onUpdate={updateOwnMembership}
        onClose={closeJoinDialog}
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
};

export default ConnectedUserActions;
