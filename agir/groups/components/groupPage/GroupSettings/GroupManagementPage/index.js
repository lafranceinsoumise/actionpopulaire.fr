import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { animated, useTransition } from "react-spring";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";
import MainPanel from "./MainPanel";
import EditionPanel from "./EditionPanel";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { Toast, TOAST_TYPES } from "@agir/front/globalContext/Toast.js";

import {
  getGroupPageEndpoint,
  updateMember,
} from "@agir/groups/groupPage/api.js";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

const [REFERENT, MANAGER /*, MEMBER */] = [100, 50, 10];

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

  const group = useGroup(groupPk);
  const { data: members, mutate } = useSWR(
    getGroupPageEndpoint("getMembers", { groupPk })
  );

  const [selectedMembershipType, setSelectedMembershipType] = useState(null);
  const [errors, setErrors] = useState({});
  const [selectedMember, setSelectedMember] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const is2022 = useMemo(() => group?.is2022, [group]);
  const [toasts, setToasts] = useState([]);

  const editManager = useCallback(() => {
    setSelectedMembershipType(MANAGER);
  }, []);

  const editReferent = useCallback(() => {
    setSelectedMembershipType(REFERENT);
  }, []);

  const selectMember = useCallback((e) => {
    setSelectedMember(e.value);
  }, []);

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const handleSubmit = useCallback(async () => {
    setErrors({});
    setIsLoading(true);
    const res = await updateMember(selectedMember.id, {
      membershipType: selectedMembershipType,
    });
    setIsLoading(false);
    if (res.error) {
      setErrors(res.error);
      return;
    }
    setToasts([
      {
        message: "Informations mises à jour",
        type: TOAST_TYPES.SUCCESS,
      },
    ]);
    setSelectedMembershipType(null);
    setSelectedMember(null);
    mutate((members) =>
      members.map((member) => (member.id === res.data.id ? res.data : member))
    );
  }, [mutate, selectedMember, selectedMembershipType]);

  const handleBack = useCallback(() => {
    setSelectedMember(null);
    setSelectedMembershipType(null);
    setErrors({});
  }, []);

  const transition = useTransition(selectedMembershipType, slideInTransition);

  return (
    <PageFadeIn ready={Array.isArray(members)}>
      <MainPanel
        onBack={onBack}
        editManager={editManager}
        editReferent={editReferent}
        illustration={illustration}
        members={members}
        is2022={is2022}
      />
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
      <Toast autoClose onClear={clearToasts} toasts={toasts} />
    </PageFadeIn>
  );
};

GroupManagementPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};

export default GroupManagementPage;
