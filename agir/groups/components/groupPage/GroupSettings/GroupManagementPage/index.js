import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useTransition } from "@react-spring/web";
import useSWR from "swr";

import { ManagerMainPanel, ReferentMainPanel } from "./MainPanel";
import EditionPanel from "./EditionPanel";
import { useToast } from "@agir/front/globalContext/hooks.js";

import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";
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
        {group?.isReferent ? (
          <ReferentMainPanel
            onBack={onBack}
            editManager={editManager}
            editReferent={editReferent}
            illustration={illustration}
            members={members || []}
            routes={group?.routes}
            onResetMembershipType={resetMembershipType}
            isLoading={isLoading}
          />
        ) : (
          <ManagerMainPanel group={group} />
        )}
      </PageFadeIn>
      {transition(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              <EditionPanel
                members={members}
                onBack={handleBack}
                onSubmit={handleSubmit}
                selectMember={selectMember}
                selectedMember={selectedMember}
                selectedMembershipType={item}
                errors={errors}
                isLoading={isLoading}
              />
            </PanelWrapper>
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
