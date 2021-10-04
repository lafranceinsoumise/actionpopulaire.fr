import PropTypes from "prop-types";
import React, { useMemo } from "react";

import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import Spacer from "@agir/front/genericComponents/Spacer";

import GroupMemberCard from "./GroupMemberCard";
import GroupMemberFacts from "./GroupMemberFacts";
import GroupMemberActions from "./GroupMemberActions";

const GroupMemberFile = (props) => {
  const { member, onBack, onChangeMembershipType, isReferent } = props;
  const hasFacts = useMemo(
    () =>
      [member.is2022, member.hasGroupNotifications, member.isLiaison].some(
        (i) => typeof i === "boolean"
      ),
    [member]
  );
  return (
    <div>
      <BackButton onClick={onBack} />
      <Spacer size="1.5rem" />
      <GroupMemberCard
        id={member.id}
        displayName={member.displayName}
        firstName={member.firstName}
        lastName={member.lastName}
        gender={member.gender}
        image={member.image}
        email={member.email}
        phone={member.phone}
        address={member.address}
        created={member.created}
        membershipType={member.membershipType}
        subscriber={member.subscriber}
      />
      {hasFacts && (
        <>
          <Spacer size="1.5rem" />
          <GroupMemberFacts
            is2022={member.is2022}
            isLiaison={member.isLiaison}
            hasGroupNotifications={member.hasGroupNotifications}
          />
        </>
      )}
      <Spacer size="1.5rem" />
      <GroupMemberActions
        currentMembershipType={member.membershipType}
        isReferent={isReferent}
        onChangeMembershipType={onChangeMembershipType}
      />
      <Spacer size="1.5rem" />
      <p
        css={`
          color: ${({ theme }) => theme.black700};
        `}
      >
        Cette personne a transmis ces informations volontairement à votre
        groupe. Elles sont strictement confidentielles.
      </p>
    </div>
  );
};

GroupMemberFile.propTypes = {
  member: PropTypes.shape({
    id: PropTypes.number,
    displayName: PropTypes.string,
    firstName: PropTypes.string,
    lastName: PropTypes.string,
    gender: PropTypes.string,
    image: PropTypes.string,
    email: PropTypes.string,
    phone: PropTypes.string,
    address: PropTypes.string,
    created: PropTypes.string,
    membershipType: PropTypes.number,
    subscriber: PropTypes.string,
    is2022: PropTypes.bool,
    isLiaison: PropTypes.bool,
    hasGroupNotifications: PropTypes.bool,
  }),
  isReferent: PropTypes.bool,
  onBack: PropTypes.func,
  onChangeMembershipType: PropTypes.func,
};

export default GroupMemberFile;
