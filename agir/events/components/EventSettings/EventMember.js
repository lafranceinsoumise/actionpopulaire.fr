import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { FaMicrophone, FaLock } from "@agir/front/genericComponents/FaIcon";

import * as style from "@agir/front/genericComponents/_variables.scss";

import Avatar from "@agir/front/genericComponents/Avatar";
import { GENDER, getGenderedWord } from "@agir/lib/utils/display";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";

const Name = styled.span``;
const Role = styled.span``;
const ResetMembershipType = styled.button``;
const Email = styled.button``;
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
    padding: 0;
    border: none;
    background-color: transparent;
    text-align: left;
    color: ${style.black500};
    font-weight: 400;
    font-size: 0.875rem;
    cursor: pointer;

    @media (min-width: ${style.collapse}px) {
      grid-column: 2/3;
      grid-row: 2/3;
    }
  }
`;

const MEMBER_TYPE_CONFIG = {
  organizer: {
    label: ["Organisateur·ice", "Organisatrice", "Organisateur"],
    icon: <FaLock />,
  },
  speaker: {
    label: ["Intervenant·e", "Intervenante", "Intervenant"],
    icon: <FaMicrophone />,
  },
};

const EventMember = (props) => {
  const {
    displayName,
    image = "",
    isOrganizer,
    isEventSpeaker,
    email,
    gender,
  } = props;

  const [_, handleCopy] = useCopyToClipboard(
    email,
    2000,
    "L'adresse e-mail a été copié",
  );

  const memberTypeConfig = useMemo(() => {
    const config = isOrganizer
      ? MEMBER_TYPE_CONFIG.organizer
      : isEventSpeaker
        ? MEMBER_TYPE_CONFIG.speaker
        : null;
    if (!config) {
      return {};
    }
    if (Array.isArray(config.label)) {
      return { ...config, label: getGenderedWord(gender, ...config.label) };
    }
    return config;
  }, [isOrganizer, isEventSpeaker, gender]);

  return (
    <Member>
      <Avatar image={image} name={displayName} />
      <Role>
        {memberTypeConfig?.label && (
          <span>
            {memberTypeConfig.icon}&ensp;{memberTypeConfig.label}
          </span>
        )}
      </Role>
      <Name>{displayName}</Name>
      <Email title="Copier l'adresse" type="button" onClick={handleCopy}>
        {email}
      </Email>
    </Member>
  );
};
EventMember.propTypes = {
  id: PropTypes.string,
  displayName: PropTypes.string,
  image: PropTypes.string,
  email: PropTypes.string,
  isOrganizer: PropTypes.bool,
  isEventSpeaker: PropTypes.bool,
  gender: PropTypes.oneOf(["", ...Object.values(GENDER)]),
};

export default EventMember;
