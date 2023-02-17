import PropTypes from "prop-types";
import React, { Fragment, useCallback, useState } from "react";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";
import useSWR from "swr";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";

import ConfirmMembershipTypeChange from "@agir/groups/groupPage/GroupSettings/ConfirmMembershipTypeChange";
import GroupMemberFile from "@agir/groups/groupPage/GroupSettings/GroupMemberFile";

import { useToast } from "@agir/front/globalContext/hooks";
import { useGroup } from "@agir/groups/groupPage/hooks/group";
import { getGroupEndpoint, updateMember } from "@agir/groups/utils/api";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const StyledSkeleton = styled.div`
  & > * {
    background-color: ${(props) => props.theme.black50};
    margin: 0;
    width: 100%;
  }

  & > :first-child {
    height: 37px;
    margin: 0.5rem 0;
  }

  & > :nth-child(2) {
    height: 56px;
    margin-bottom: 2rem;
  }

  & > :last-child {
    height: 177px;
  }
`;

const SecondaryPanel = styled(animated.div)`
  position: absolute;
  top: 0;
  left: 0;
  padding: 1.5rem;
  z-index: 1;
  background-color: white;
  width: 100%;
  height: 100%;
  box-shadow: ${(props) => props.theme.elaborateShadow};
`;

const MembersSkeleton = (
  <StyledSkeleton aria-hidden="true">
    <div />
    <div />
    <div />
  </StyledSkeleton>
);

export const ReadOnlyMembershipPanel = (props) => {
  const { groupPk, illustration, MainPanel, onBack } = props;
  const group = useGroup(groupPk);
  const { data: members, isLoading: groupIsLoading } = useSWR(
    getGroupEndpoint("getMembers", { groupPk })
  );

  const [selectedMember, setSelectedMember] = useState(null);

  const { data: selectedMemberData } = useSWR(
    selectedMember?.id &&
      getGroupEndpoint("getMemberPersonalInformation", {
        memberPk: selectedMember?.id,
      })
  );

  const selectMember = useCallback(
    (memberId) => {
      const member = members.find((member) => member.id === memberId);
      setSelectedMember(member);
    },
    [members]
  );

  const unselectMember = useCallback(() => {
    setSelectedMember(null);
  }, []);

  const memberFileTransition = useTransition(
    !!selectedMemberData,
    slideInTransition
  );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <PageFadeIn ready={Array.isArray(members)} wait={MembersSkeleton}>
        <MainPanel
          group={group}
          members={members}
          routes={group?.routes}
          isLoading={groupIsLoading}
          onClickMember={selectMember}
        />
        {memberFileTransition(
          (style, item) =>
            item && (
              <SecondaryPanel style={style}>
                <GroupMemberFile
                  isGroupFull={!!group.isFull}
                  isReferent={group.isReferent}
                  member={selectedMemberData}
                  onBack={unselectMember}
                />
              </SecondaryPanel>
            )
        )}
      </PageFadeIn>
    </>
  );
};

ReadOnlyMembershipPanel.propTypes = {
  groupPk: PropTypes.string,
  members: PropTypes.array,
  illustration: PropTypes.string,
  MainPanel: PropTypes.elementType,
  onBack: PropTypes.func,
};

const EditableMembershipPanel = (props) => {
  const {
    groupPk,
    illustration,
    MainPanel,
    onBack,
    unselectMemberAfterUpdate = false,
  } = props;
  const sendToast = useToast();

  const group = useGroup(groupPk);
  const { data: members, mutate: mutateMembers } = useSWR(
    getGroupEndpoint("getMembers", { groupPk })
  );

  const [selectedMembershipType, setSelectedMembershipType] = useState(null);
  const [selectedMember, setSelectedMember] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    data: selectedMemberPersonalInformation,
    mutate: mutateSelectedMember,
  } = useSWR(
    selectedMember?.id &&
      getGroupEndpoint("getMemberPersonalInformation", {
        memberPk: selectedMember?.id,
      })
  );

  const updateMembershipType = useCallback(
    async (memberId, membershipType) => {
      setIsLoading(true);
      const res = await updateMember(memberId, {
        membershipType: membershipType,
      });
      setIsLoading(false);
      setSelectedMembershipType(null);
      unselectMemberAfterUpdate && setSelectedMember(null);
      if (res.error) {
        sendToast(
          res.error?.membershipType ||
            "Une erreur est survenue. Veuillez ressayer.",
          "ERROR",
          { autoClose: true }
        );
        return;
      }
      sendToast("Informations mises à jour", "SUCCESS", {
        autoClose: true,
      });
      !unselectMemberAfterUpdate && mutateSelectedMember();
      mutateMembers((members) =>
        members.map((member) => (member.id === res.data.id ? res.data : member))
      );
    },
    [unselectMemberAfterUpdate, mutateMembers, mutateSelectedMember, sendToast]
  );

  const updateMembership = useCallback(() => {
    updateMembershipType(selectedMember.id, selectedMembershipType);
  }, [selectedMember, selectedMembershipType, updateMembershipType]);

  const selectMember = useCallback(
    (memberId) => {
      const member = members.find((member) => member.id === memberId);
      setSelectedMember(member);
    },
    [members]
  );

  const unselectMember = useCallback(() => {
    setSelectedMember(null);
  }, []);

  const selectMembershipType = useCallback((membershipType) => {
    setSelectedMembershipType(membershipType);
  }, []);

  const unselectMembershipType = useCallback(() => {
    setSelectedMembershipType(null);
  }, []);

  const memberFileTransition = useTransition(
    !!selectedMemberPersonalInformation,
    slideInTransition
  );
  const confirmTransition = useTransition(
    selectedMembershipType,
    slideInTransition
  );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <PageFadeIn ready={Array.isArray(members)} wait={MembersSkeleton}>
        <MainPanel
          group={group}
          members={members}
          routes={group?.routes}
          onClickMember={selectMember}
          isLoading={isLoading}
          updateMembershipType={updateMembershipType}
        />
      </PageFadeIn>
      {memberFileTransition(
        (style, item) =>
          item && (
            <SecondaryPanel style={style}>
              <GroupMemberFile
                isGroupFull={!!group.isFull}
                isReferent={group.isReferent}
                member={selectedMemberPersonalInformation}
                onBack={unselectMember}
                onChangeMembershipType={selectMembershipType}
              />
            </SecondaryPanel>
          )
      )}
      {confirmTransition(
        (style, item) =>
          item && (
            <SecondaryPanel style={style}>
              <ConfirmMembershipTypeChange
                members={members}
                onBack={unselectMembershipType}
                onConfirm={updateMembership}
                selectedMember={selectedMemberPersonalInformation}
                selectedMembershipType={item}
                isLoading={isLoading}
              />
            </SecondaryPanel>
          )
      )}
    </>
  );
};

EditableMembershipPanel.propTypes = {
  groupPk: PropTypes.string,
  illustration: PropTypes.string,
  MainPanel: PropTypes.elementType,
  unselectMemberAfterUpdate: PropTypes.bool,
  onBack: PropTypes.func,
};

export default EditableMembershipPanel;
