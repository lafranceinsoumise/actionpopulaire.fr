import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import { FaUserCheck, FaLock } from "react-icons/fa";

import style from "@agir/front/genericComponents/_variables.scss";

import { GENDER, getGenderedWord } from "@agir/lib/utils/display";
import Avatar from "@agir/front/genericComponents/Avatar";

const Name = styled.span``;
const Role = styled.span``;
const ResetMembershipType = styled.button``;
const Email = styled.span``;
const Member = styled.div`
  background-color: ${style.white};
  padding: 0.75rem 1rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-rows: auto auto;
  align-items: center;
  grid-gap: 0 1rem;

  @media (max-width: ${style.collapse}px) {
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto auto;
  }

  & > * {
    margin: 0;
  }

  ${Avatar} {
    grid-row: span 2;
    width: 2rem;
    height: 2rem;

    @media (max-width: ${style.collapse}px) {
      grid-row: span 3;
      width: 1.5rem;
      height: 1.5rem;
      align-self: start;
    }
  }

  ${Role} {
    color: ${style.green500};
    font-size: 0.813rem;
    text-align: right;
    display: flex;
    flex-flow: row wrap;
    align-items: center;

    @media (min-width: ${style.collapse}px) {
      grid-column: 3/4;
      grid-row: span 2;
      flex-flow: column nowrap;
    }

    &:empty {
      display: none;
    }

    span {
      display: flex;
      align-items: center;
      padding-right: 1rem;
      margin-right: auto;

      @media (min-width: ${style.collapse}px) {
        justify-content: flex-end;
      }
    }

    ${ResetMembershipType} {
      padding: 0;
      border: none;
      outline: none;
      background-color: transparent;
      text-decoration: underline;
      font-size: inherit;
      color: ${style.black500};
      cursor: pointer;
    }
  }

  ${Name} {
    font-weight: 500;

    @media (min-width: ${style.collapse}px) {
      grid-column: 2/3;
      grid-row: 1/2;
    }
  }
  ${Email} {
    color: ${style.black500};
    font-weight: 400;
    font-size: 0.875rem;

    @media (min-width: ${style.collapse}px) {
      grid-column: 2/3;
      grid-row: 2/3;
    }
  }
`;

const MEMBERSHIP_TYPE_LABEL = {
  10: "",
  50: "Gestionnaire",
  100: ["Animateur·ice", "Animatrice", "Animateur"],
};

const MEMBERSHIP_TYPE_ICON = {
  // 10: null,
  50: <FaUserCheck />,
  100: <FaLock />,
};

const GroupMember = (props) => {
  const {
    id,
    displayName,
    image = "",
    membershipType,
    email,
    gender,
    onResetMembershipType,
  } = props;

  const handleResetMembershipType = useCallback(() => {
    onResetMembershipType && onResetMembershipType(id);
  }, [onResetMembershipType, id]);

  const role = useMemo(() => {
    const label = MEMBERSHIP_TYPE_LABEL[String(membershipType)];
    if (!label) {
      return "";
    }
    if (Array.isArray(label)) {
      return getGenderedWord(gender, ...label);
    }
    return label;
  }, [membershipType, gender]);

  return (
    <Member>
      <Avatar image={image} name={displayName} />
      <Role>
        {role && (
          <span>
            {MEMBERSHIP_TYPE_ICON[membershipType]}&ensp;{role}
          </span>
        )}
        {typeof onResetMembershipType === "function" && (
          <ResetMembershipType onClick={handleResetMembershipType}>
            Retirer le droit
          </ResetMembershipType>
        )}
      </Role>
      <Name>{displayName}</Name>
      <Email>{email}</Email>
    </Member>
  );
};
GroupMember.propTypes = {
  id: PropTypes.number,
  displayName: PropTypes.string,
  image: PropTypes.string,
  email: PropTypes.string,
  membershipType: PropTypes.oneOf(
    Object.keys(MEMBERSHIP_TYPE_LABEL).map(Number)
  ),
  gender: PropTypes.oneOf(["", ...Object.values(GENDER)]),
  onResetMembershipType: PropTypes.func,
};

export default GroupMember;
