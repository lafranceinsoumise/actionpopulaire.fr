import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Avatar from "@agir/front/genericComponents/Avatar";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
import Spacer from "@agir/front/genericComponents/Spacer";

import { timeAgo } from "@agir/lib/utils/time";
import { GENDER } from "@agir/lib/utils/display";
import {
  MEMBERSHIP_TYPES,
  MEMBERSHIP_TYPE_ICON,
  getGenderedMembershipType,
} from "@agir/groups/utils/group";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";

const StyledCard = styled.div`
  padding: 1rem;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};
  background: linear-gradient(
    180deg,
    ${(props) => props.theme.primary50} 0px,
    ${(props) => props.theme.primary50} 4.375rem,
    ${(props) => props.theme.white} 4.375rem
  );

  header {
    ${Avatar} {
      width: 5rem;
      height: 5rem;
      border: 3px solid ${(props) => props.theme.white};
    }

    h4 {
      display: flex;
      flex-flow: row wrap;
      gap: 0.5rem 1rem;
      align-items: center;
      margin: 0;

      small {
        font-weight: 400;
        font-size: 0.875rem;
        line-height: 0;
        color: ${(props) => props.theme.black500};
        display: inline-flex;
        align-items: center;
        height: 29px;
        padding: 0 0.5rem;
        border: 1px solid ${(props) => props.theme.black500};
        border-radius: ${(props) => props.theme.borderRadius};

        svg {
          stroke-width: 2;
        }
      }
    }
  }

  div {
    p {
      font-weight: 400;
      font-size: 1rem;
      line-height: 1.5;
      margin: 0;
      display: flex;
      flex-flow: row wrap;
      gap: 0.5rem 1rem;
      align-items: center;

      & > button {
        cursor: pointer;
        padding: 0;
        text-align: left;
        background-color: transparent;
        border: none;
      }

      & > span,
      & > button {
        display: inline-flex;
        align-items: center;

        svg {
          color: ${(props) => props.theme.black500};
          stroke-width: 2;
        }
      }

      a,
      strong {
        font-weight: 500;
        color: ${(props) => props.theme.primary500};
      }

      a,
      a:hover,
      &:focus {
        text-decoration: none;
      }
    }

    p + p {
      margin-top: 0.5rem;
    }
  }
`;

const GroupMemberCard = (props) => {
  const {
    displayName,
    firstName,
    lastName,
    gender,
    image,
    email,
    phone,
    address,
    created,
    membershipType,
    subscriber,
    meta = {},
  } = props;

  const [_, handleCopy] = useCopyToClipboard(
    email,
    2000,
    "L'adresse e-mail a été copié."
  );

  const role = useMemo(
    () => getGenderedMembershipType(membershipType, gender),
    [membershipType, gender]
  );

  const { description, group_id, group_name } = meta;

  return (
    <StyledCard>
      <header>
        <Avatar name={displayName} image={image} />
        <Spacer size=".5rem" />
        <h4>
          {firstName || lastName
            ? `${firstName} ${lastName}`.trim()
            : displayName}
          <small>
            <FeatherIcon
              name={MEMBERSHIP_TYPE_ICON[String(membershipType)]}
              small
            />
            &nbsp;
            <span>{role}</span>
          </small>
        </h4>
      </header>
      <Spacer size=".5rem" />
      <div>
        <p>
          {phone ? (
            <span>
              <FeatherIcon small name="phone" />
              &ensp;<a href={`tel:${phone}`}>{phone}</a>
            </span>
          ) : null}
          {email ? (
            <button type="button" title="Copier l'adresse" onClick={handleCopy}>
              <FeatherIcon small name="mail" />
              &ensp;<strong>{email}</strong>
            </button>
          ) : null}
        </p>
        {address ? (
          <p>
            <span>
              <FeatherIcon small name="map-pin" />
              &ensp;{address}
            </span>
          </p>
        ) : null}
        <p>
          <span>
            <FeatherIcon small name="clock" />
            &ensp;
            {membershipType === MEMBERSHIP_TYPES.FOLLOWER
              ? `Contact ${subscriber ? "ajouté" : "depuis"} ${
                  timeAgo(created, "day").split(" à ")[0]
                }
            ${subscriber ? ` par ${subscriber}` : ""}`
              : `Membre du groupe depuis ${
                  timeAgo(created, "day").split(" à ")[0]
                }`}
          </span>
        </p>
        {description && (
          <>
            <p>
              <span>
                <FeatherIcon small name="info" />
                &ensp;
                {description}
              </span>
            </p>
            {group_id && group_name ? (
              <p>
                <span>
                  <FeatherIcon small name="users" />
                  &ensp;
                  <Link
                    route="groupDetails"
                    routeParams={{ groupPk: group_id }}
                  >
                    {group_name}
                  </Link>
                </span>
              </p>
            ) : null}
          </>
        )}
      </div>
    </StyledCard>
  );
};

GroupMemberCard.propTypes = {
  id: PropTypes.number.isRequired,
  displayName: PropTypes.string.isRequired,
  firstName: PropTypes.string,
  lastName: PropTypes.string,
  gender: PropTypes.oneOf(Object.values(GENDER)).isRequired,
  image: PropTypes.string,
  email: PropTypes.string.isRequired,
  phone: PropTypes.string,
  address: PropTypes.string,
  created: PropTypes.string.isRequired,
  membershipType: PropTypes.oneOf(Object.values(MEMBERSHIP_TYPES)).isRequired,
  subscriber: PropTypes.string,
  meta: PropTypes.shape({
    description: PropTypes.string,
    group_id: PropTypes.string,
    group_name: PropTypes.string,
  }),
};

export default GroupMemberCard;
