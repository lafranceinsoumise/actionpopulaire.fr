import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";
import MainPanel from "./MainPanel";
import EditionPanel from "./EditionPanel";
import { useToast } from "@agir/front/globalContext/hooks.js";

import HeaderPanel from "@agir/groups/groupPage/GroupSettings/HeaderPanel";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import {
  getGroupPageEndpoint,
  updateMember,
} from "@agir/groups/groupPage/api.js";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

const [REFERENT, MANAGER, MEMBER] = [100, 50, 10];

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const EditionPanelWrapper = styled(animated.div)`
  position: absolute;
  top: 0;
  left: 0;
  padding: 2rem;
  background-color: white;
  width: 100%;
  height: 100%;
  box-shadow: ${style.elaborateShadow};
  will-change: transform;
`;

const GroupManagementPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const sendToast = useToast();

  const group = useGroup(groupPk);
  const { data: members, mutate } = useSWR(
    getGroupPageEndpoint("getMembers", { groupPk })
  );
  const [selectedMembershipType, setSelectedMembershipType] = useState(null);
  const [errors, setErrors] = useState({});
  const [selectedMember, setSelectedMember] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const is2022 = useMemo(() => group?.is2022, [group]);

  const editManager = useCallback(() => {
    setSelectedMembershipType(MANAGER);
  }, []);

  const editReferent = useCallback(() => {
    setSelectedMembershipType(REFERENT);
  }, []);

  const selectMember = useCallback((option) => {
    option && setSelectedMember(option.value);
  }, []);

  const updateMembershipType = useCallback(
    async (memberId, membershipType) => {
      setErrors({});
      setIsLoading(true);
      const res = await updateMember(memberId, {
        membershipType: membershipType,
      });
      setIsLoading(false);
      if (res.error) {
        setErrors(res.error);
        return;
      }
      sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
      setSelectedMembershipType(null);
      setSelectedMember(null);
      mutate((members) =>
        members.map((member) => (member.id === res.data.id ? res.data : member))
      );
    },
    [mutate, sendToast]
  );

  const handleSubmit = useCallback(() => {
    updateMembershipType(selectedMember.id, selectedMembershipType);
  }, [selectedMember, selectedMembershipType, updateMembershipType]);

  const resetMembershipType = useCallback(
    (memberId) => {
      updateMembershipType(memberId, MEMBER);
    },
    [updateMembershipType]
  );

  const handleBack = useCallback(() => {
    setSelectedMember(null);
    setSelectedMembershipType(null);
    setErrors({});
  }, []);

  const transition = useTransition(selectedMembershipType, slideInTransition);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <PageFadeIn ready={Array.isArray(members)} wait={<Skeleton />}>
        <MainPanel
          onBack={onBack}
          editManager={editManager}
          editReferent={editReferent}
          illustration={illustration}
          members={members || []}
          is2022={is2022}
          routes={group?.routes}
          onResetMembershipType={resetMembershipType}
          isLoading={isLoading}
          group={group}
        />
      </PageFadeIn>
      {transition(
        (style, item) =>
          item && (
            <EditionPanelWrapper style={style}>
              <EditionPanel
                members={members}
                onBack={handleBack}
                onSubmit={handleSubmit}
                selectMember={selectMember}
                selectedMember={selectedMember}
                selectedMembershipType={item}
                errors={errors}
                isLoading={isLoading}
                is2022={is2022}
              />
            </EditionPanelWrapper>
          )
      )}
    </>
  );
};

GroupManagementPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};

export default GroupManagementPage;
