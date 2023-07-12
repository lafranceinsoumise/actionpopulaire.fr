import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useTransition } from "@react-spring/web";

import ManagerMainPanel from "./ManagerMainPanel";
import ReferentMainPanel from "./ReferentMainPanel";
import EditionPanel from "./EditionPanel";

import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const GroupManagementPage = (props) => {
  const {
    group,
    members,
    routes,
    onClickMember,
    isLoading,
    updateMembershipType,
  } = props;

  const [selectedMembershipType, setSelectedMembershipType] = useState(null);
  const [selectedMember, setSelectedMember] = useState(null);

  const addManager = useCallback(() => {
    setSelectedMembershipType(MEMBERSHIP_TYPES.MANAGER);
  }, []);
  const addReferent = useCallback(() => {
    setSelectedMembershipType(MEMBERSHIP_TYPES.REFERENT);
  }, []);
  const selectMember = useCallback((option) => {
    option && setSelectedMember(option.value);
  }, []);

  const handleSubmit = useCallback(() => {
    updateMembershipType(selectedMember.id, selectedMembershipType);
    setSelectedMember(null);
    setSelectedMembershipType(null);
  }, [selectedMember, selectedMembershipType, updateMembershipType]);

  const handleBack = useCallback(() => {
    setSelectedMember(null);
    setSelectedMembershipType(null);
  }, []);

  const transition = useTransition(selectedMembershipType, slideInTransition);

  return (
    <>
      {group.isReferent ? (
        <ReferentMainPanel
          onClickMember={onClickMember}
          addManager={addManager}
          addReferent={addReferent}
          members={members || []}
          isLoading={isLoading}
          routes={routes}
        />
      ) : (
        <ManagerMainPanel group={group} />
      )}
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
                isLoading={isLoading}
              />
            </PanelWrapper>
          ),
      )}
    </>
  );
};

GroupManagementPage.propTypes = {
  group: PropTypes.object,
  members: PropTypes.arrayOf(PropTypes.object),
  routes: PropTypes.object,
  onClickMember: PropTypes.func,
  updateMembershipType: PropTypes.func,
  isLoading: PropTypes.bool,
};

export default GroupManagementPage;
