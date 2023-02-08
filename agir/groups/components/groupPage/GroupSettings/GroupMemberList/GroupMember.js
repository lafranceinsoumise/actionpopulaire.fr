import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { GENDER, getGenderedWord } from "@agir/lib/utils/display";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

const StyledName = styled.p``;
const StyledEmail = styled.p``;
const StyledDescription = styled.p``;
const StyledMembershipType = styled.p``;

const StyledMember = styled.div`
  background-color: ${style.white};
  padding: 0.75rem 1rem;
  display: grid;
  grid-template-columns: auto 1fr max-content auto;
  grid-template-rows: auto auto auto;
  align-items: center;
  gap: 0 1rem;
  width: 100%;
  text-align: left;
  cursor: ${(props) => (props.as === "button" ? "pointer" : "default")};

  &[disabled] {
    cursor: default;
  }

  & > * {
    margin: 0;
  }

  ${Avatar} {
    grid-column: 1/2;
    grid-row: 1/3;
    width: 2rem;
    height: 2rem;

    @media (max-width: ${style.collapse}px) {
      width: 1.5rem;
      height: 1.5rem;
    }

    @media (max-width: 350px) {
      display: none;
    }
  }

  ${StyledName},
  ${StyledEmail},
  ${StyledDescription} {
    margin: 0;
    padding: 0;
    min-width: 1px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;

    &:empty {
      display: none;
      min-width: 0;
    }
  }

  ${StyledName} {
    grid-column: 2/3;
    grid-row: 1/2;
    font-weight: 500;
  }

  ${StyledEmail} {
    grid-column: 2/3;
    grid-row: 2/3;
    color: ${style.black500};
    font-weight: 400;
    font-size: 0.875rem;
  }

  ${StyledDescription} {
    grid-column: 2/5;
    grid-row: 3/4;
    color: ${style.black500};
    font-weight: 400;
    font-size: 0.75rem;

    &::before {
      content: "— ";

      @media (max-width: 350px) {
        display: none;
      }
    }
  }

  ${StyledMembershipType} {
    grid-column: 3/4;
    grid-row: 1/3;
    text-align: right;
    color: ${style.black1000};
    display: inline-flex;
    flex-flow: row nowrap;
    align-items: center;
    min-width: 1px;

    @media (max-width: ${style.collapse}px) {
      font-size: 0.813rem;
    }

    & > * {
      line-height: 1;
    }

    ${RawFeatherIcon} {
      width: 1rem;
      height: 1rem;

      @media (max-width: ${style.collapse}px) {
        width: 0.813rem;
        height: 0.813rem;
      }
    }
  }

  ${StyledMembershipType} + * {
    grid-column: 4/5;
    grid-row: 1/3;
    width: 2rem;
    height: 2rem;

    @media (max-width: 350px) {
      display: none;
    }
  }
`;

const MEMBERSHIP_TYPE_LABEL = {
  [MEMBERSHIP_TYPES.FOLLOWER]: ["Abonné·e", "Abonnée", "Abonné"],
  [MEMBERSHIP_TYPES.MEMBER]: "Membre actif",
  [MEMBERSHIP_TYPES.MANAGER]: "Gestionnaire",
  [MEMBERSHIP_TYPES.REFERENT]: ["Animateur·ice", "Animatrice", "Animateur"],
};

const MembershipType = ({ gender, membershipType, hasGroupNotifications }) => {
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

  switch (membershipType) {
    case MEMBERSHIP_TYPES.FOLLOWER:
      return hasGroupNotifications ? (
        <StyledMembershipType style={{ color: style.black500 }}>
          <RawFeatherIcon name="rss" small />
          &ensp;
          <span>{role}</span>
        </StyledMembershipType>
      ) : null;
    case MEMBERSHIP_TYPES.MANAGER:
      return (
        <StyledMembershipType style={{ color: style.green500 }}>
          <RawFeatherIcon name="settings" small />
          &ensp;
          <span>{role}</span>
        </StyledMembershipType>
      );
    case MEMBERSHIP_TYPES.REFERENT:
      return (
        <StyledMembershipType style={{ color: style.primary500 }}>
          <RawFeatherIcon name="lock" small />
          &ensp;
          <span>{role}</span>
        </StyledMembershipType>
      );
    default:
      return null;
  }
};

MembershipType.propTypes = {
  membershipType: PropTypes.oneOf(
    Object.keys(MEMBERSHIP_TYPE_LABEL).map(Number)
  ).isRequired,
  gender: PropTypes.oneOf(["", ...Object.values(GENDER)]),
  hasGroupNotifications: PropTypes.bool,
};

const GroupMember = (props) => {
  const {
    id,
    displayName,
    image = "",
    description,
    membershipType,
    email,
    gender,
    hasGroupNotifications,
    onClick,
    isLoading,
  } = props;

  const handleClick = () => {
    onClick && onClick(id);
  };

  return (
    <StyledMember
      onClick={handleClick}
      disabled={isLoading}
      type={typeof onClick === "function" ? "button" : undefined}
      as={typeof onClick === "function" ? "button" : "div"}
    >
      <Avatar image={image} name={displayName} />
      <StyledName>{displayName}</StyledName>
      <StyledEmail>{email}</StyledEmail>
      <StyledDescription>{description}</StyledDescription>
      <MembershipType
        gender={gender}
        membershipType={membershipType}
        hasGroupNotifications={hasGroupNotifications}
      />
      {typeof onClick === "function" ? (
        <RawFeatherIcon name="arrow-right" />
      ) : (
        <Spacer size="2rem" />
      )}
    </StyledMember>
  );
};
GroupMember.propTypes = {
  id: PropTypes.number,
  displayName: PropTypes.string,
  image: PropTypes.string,
  email: PropTypes.string,
  description: PropTypes.string,
  membershipType: PropTypes.oneOf([
    MEMBERSHIP_TYPES.FOLLOWER,
    MEMBERSHIP_TYPES.MEMBER,
    MEMBERSHIP_TYPES.REFERENT,
    MEMBERSHIP_TYPES.MANAGER,
  ]).isRequired,
  gender: PropTypes.oneOf(["", ...Object.values(GENDER)]),
  onClick: PropTypes.func,
  isLoading: PropTypes.bool,
  hasGroupNotifications: PropTypes.bool,
};

export default GroupMember;
