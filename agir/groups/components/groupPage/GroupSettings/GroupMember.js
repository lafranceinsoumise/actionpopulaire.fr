import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { GENDER, getGenderedWord } from "@agir/lib/utils/display";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import InlineMenu from "@agir/front/genericComponents/InlineMenu";
import Spacer from "@agir/front/genericComponents/Spacer";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";

const Name = styled.span``;
const Role = styled.span``;
const Email = styled.span``;

const InlineMenuList = styled.ul`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  list-style: none;
  color: ${style.primary500};
  padding: 0;
  margin: 0;
  font-size: 0.875rem;

  @media (max-width: ${style.collapse}px) {
    padding: 1.5rem;
    font-size: 1rem;
  }

  button,
  button:focus,
  button:hover {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    text-align: left;
    white-space: nowrap;
    cursor: pointer;
    background-color: transparent;
    outline: none;
    border: none;
    font-size: inherit;
    color: ${style.black1000};

    ${RawFeatherIcon} {
      width: 0.875rem;
      height: 0.875rem;

      @media (max-width: ${style.collapse}px) {
        width: 1rem;
        height: 1rem;
      }
    }
  }
`;

const Member = styled.div`
  background-color: ${style.white};
  padding: 0.75rem 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0 1rem;

  & > * {
    margin: 0;
    flex: 0 0 auto;
  }

  ${Avatar} {
    align-self: center;
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

  ${Name} {
    flex: 1 1 auto;
    font-weight: 500;
    min-width: 1px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  ${Email} {
    display: block;
    color: ${style.black500};
    font-weight: 400;
    font-size: 0.875rem;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  ${Role} {
    text-align: right;
    color: ${style.black1000};
    display: inline-flex;
    flex-flow: row nowrap;
    align-items: center;

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
`;

const MEMBERSHIP_TYPE_LABEL = {
  [MEMBERSHIP_TYPES.FOLLOWER]: ["Abonné·e", "Abonnée", "Abonné"],
  [MEMBERSHIP_TYPES.MEMBER]: "Membre actif",
  [MEMBERSHIP_TYPES.MANAGER]: "Gestionnaire",
  [MEMBERSHIP_TYPES.REFERENT]: ["Animateur·ice", "Animatrice", "Animateur"],
};

const MembershipType = ({ gender, membershipType }) => {
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
    case 5:
      return (
        <Role style={{ color: style.black500 }}>
          <RawFeatherIcon name="rss" small />
          &ensp;
          <span>{role}</span>
        </Role>
      );
    case 10:
      return (
        <Role>
          <RawFeatherIcon name="user" small />
          &ensp;
          <span>{role}</span>
        </Role>
      );
    case 50:
      return (
        <Role style={{ color: style.green500 }}>
          <RawFeatherIcon name="settings" small />
          &ensp;
          <span>{role}</span>
        </Role>
      );
    case 100:
      return (
        <Role style={{ color: style.primary500 }}>
          <RawFeatherIcon name="lock" small />
          &ensp;
          <span>{role}</span>
        </Role>
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
};

const GroupMember = (props) => {
  const {
    id,
    displayName,
    image = "",
    membershipType,
    email,
    gender,
    onChangeMembershipType,
    onResetMembershipType,
    isLoading,
  } = props;

  const menuTriggerSize = useResponsiveMemo(1, 1.5);

  const actions = [
    onChangeMembershipType && membershipType === MEMBERSHIP_TYPES.MEMBER
      ? {
          label: (
            <>
              <RawFeatherIcon color={style.primary500} name="user-x" />
              &ensp;Retirer des membres actifs
            </>
          ),
          handler: () => {
            onChangeMembershipType(id, MEMBERSHIP_TYPES.FOLLOWER);
          },
        }
      : undefined,
    onChangeMembershipType && membershipType === MEMBERSHIP_TYPES.FOLLOWER
      ? {
          label: (
            <>
              <RawFeatherIcon color={style.primary500} name="user-check" />
              &ensp;Passer en membre actif
            </>
          ),
          handler: () => {
            onChangeMembershipType(id, MEMBERSHIP_TYPES.MEMBER);
          },
        }
      : undefined,
    onResetMembershipType
      ? {
          label: (
            <>
              <RawFeatherIcon color={style.primary500} name="eye-off" />
              &ensp;Retirer le droit
            </>
          ),
          handler: () => {
            onResetMembershipType(id);
          },
        }
      : undefined,
  ].filter(Boolean);

  return (
    <Member>
      <Avatar image={image} name={displayName} />
      <Name>
        {displayName}
        <Email>{email}</Email>
      </Name>
      <MembershipType gender={gender} membershipType={membershipType} />
      {actions.length > 0 ? (
        <InlineMenu triggerSize={`${menuTriggerSize}rem`} shouldDismissOnClick>
          <InlineMenuList>
            {actions.map((action) => (
              <li key={action.label}>
                <button disabled={isLoading} onClick={action.handler}>
                  {action.label}
                </button>
              </li>
            ))}
          </InlineMenuList>
        </InlineMenu>
      ) : (
        <Spacer size={`${menuTriggerSize + 0.5}rem`} />
      )}
    </Member>
  );
};
GroupMember.propTypes = {
  id: PropTypes.number,
  displayName: PropTypes.string,
  image: PropTypes.string,
  email: PropTypes.string,
  membershipType: PropTypes.oneOf([
    MEMBERSHIP_TYPES.FOLLOWER,
    MEMBERSHIP_TYPES.MEMBER,
    MEMBERSHIP_TYPES.REFERENT,
    MEMBERSHIP_TYPES.MANAGER,
  ]).isRequired,
  gender: PropTypes.oneOf(["", ...Object.values(GENDER)]),
  onResetMembershipType: PropTypes.func,
  onChangeMembershipType: PropTypes.func,
  isLoading: PropTypes.bool,
};

export default GroupMember;
