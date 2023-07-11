import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Modal from "@agir/front/genericComponents/Modal";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import StaticToast from "@agir/front/genericComponents/StaticToast";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import * as api from "@agir/events/common/api";
import { mutate } from "swr";

const ModalContent = styled.div`
  background: white;
  width: 50%;
  max-width: 500px;
  padding: 10px 20px;
  overflow: auto;
  margin: 5% auto;
  display: flex;
  flex-direction: column;
  border-radius: ${style.borderRadius};

  h2 {
    font-size: 18px;
    margin-top: 0;
  }

  @media (max-width: ${style.collapse}px) {
    height: max-content;
    max-height: 50%;
  }

  @media (max-width: ${style.collapse}px) {
    width: 100vw;
    height: 100vh;
    margin: 0;
    border-radius: 0;
  }
`;

const StyledIconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  width: 2rem;
  border: none;
  padding: 0;
  margin: 0;
  text-decoration: none;
  background: inherit;
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${style.black1000};
`;

const StyledModalHeader = styled.header`
  display: flex;
  justify-content: end;
`;

const GroupItem = styled.div`
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-bottom: 1rem;

  :hover {
    opacity: 0.8;
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: ${style.primary500};
    color: #fff;
    clip-path: circle(1rem);
    text-align: center;
    margin-right: 0.5rem;
  }
`;

const AddGroupAttendee = ({ id, groups, groupsAttendees }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errors, setErrors] = useState({});
  const [groupJoined, setGroupJoined] = useState(false);

  // Get groups where im manager
  const user = useSelector(getUser);

  const eventGroupsId = groups?.map((group) => group.id) || [];
  const eventGroupsAttendeesId =
    groupsAttendees?.map((group) => group.id) || [];

  const blackList = eventGroupsId.concat(eventGroupsAttendeesId);

  // Get managing groups not attendees
  const managingGroups =
    user?.groups?.filter(
      (group) => group.isManager && !blackList.includes(group.id),
    ) || [];

  const handleJoinAsGroup = async (group) => {
    setErrors({});
    const { _, error } = await api.joinEventAsGroup(id, group.id);

    if (error) {
      setErrors(error);
      return;
    }
    setGroupJoined(group);
    mutate(api.getEventEndpoint("getEvent", { eventPk: id }));
  };

  const showModalJoinAsGroup = () => {
    setIsModalOpen(true);
  };

  const closeModalJoin = () => {
    setIsModalOpen(false);
    setErrors({});
    setGroupJoined(false);
  };

  return (
    <>
      {!!managingGroups?.length && (
        <Button onClick={showModalJoinAsGroup}>
          Participer avec mon groupe
        </Button>
      )}
      <ResponsiveLayout
        DesktopLayout={Modal}
        MobileLayout={BottomSheet}
        shouldShow={isModalOpen}
        isOpen={isModalOpen}
        onClose={closeModalJoin}
        onDismiss={closeModalJoin}
        shouldDismissOnClick
        noScroll
      >
        <ModalContent>
          <StyledModalHeader>
            <StyledIconButton onClick={closeModalJoin}>
              <RawFeatherIcon name="x" />
            </StyledIconButton>
          </StyledModalHeader>
          <div>
            {!groupJoined ? (
              <>
                <h2>Participer avec mon groupe</h2>
                Ajoutez un groupe dont vous êtes gestionnaire comme participant
                à l’événement.
                <Spacer size="0.5rem" />
                L’événement sera ajouté à l’agenda du groupe.
                <Spacer size="0.5rem" />
                Les groupes participants n'ont pas de droit d'organisation de
                l'événement. Seuls les groupes co-organisateurs peuvent inviter
                d'autres groupes à co-organiser.
                <Spacer size="1rem" />
                {managingGroups.map((group) => (
                  <GroupItem
                    key={group.id}
                    onClick={() => handleJoinAsGroup(group)}
                  >
                    <RawFeatherIcon width="1rem" height="1rem" name="users" />
                    <div>{group.name}</div>
                  </GroupItem>
                ))}
                <Spacer size="1rem" />
                {!!Object.keys(errors).length && (
                  <StaticToast style={{ marginTop: 0 }}>
                    {errors?.text || "Une erreur est apparue"}
                  </StaticToast>
                )}
              </>
            ) : (
              <>
                <h2 style={{ color: style.green500 }}>
                  Votre groupe participe à l’évémenent&nbsp;!
                </h2>
                <b>{groupJoined.name}</b> est désormais indiqué comme
                participant à l’événement.
                <Spacer size="1rem" />
                Tous les membres du groupe présents doivent également indiquer
                leur présence individuelle sur Action Populaire pour aider les
                organisateur·ices à définir le nombre de participants.
                <Spacer size="1rem" />
                <Button onClick={closeModalJoin}>Compris</Button>
              </>
            )}
          </div>
        </ModalContent>
      </ResponsiveLayout>
    </>
  );
};
AddGroupAttendee.propTypes = {
  id: PropTypes.string,
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      isManager: PropTypes.bool,
    }),
  ),
  groupsAttendees: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      isManager: PropTypes.bool,
    }),
  ),
};

export default AddGroupAttendee;
