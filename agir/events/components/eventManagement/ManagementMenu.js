import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import events from "@agir/front/mockData/events.json";

const MENU_ITEMS = {
  information: {
    id: "information",
    label: "Général",
    icon: "file-text",
  },
  participants: {
    id: "participants",
    label: (event) =>
      `${(event && event.participantCount) || ""} Participant·es`.trim(),
    icon: "users",
  },
  organizerGroups: {
    id: "organizerGroups",
    label: "Co-organisation",
    icon: "settings",
  },
  rights: {
    id: "rights",
    label: "Droits",
    icon: "lock",
  },
  onlineMeeting: {
    id: "onlineMeeting",
    label: "Vidéoconférence",
    icon: "video",
  },
  contact: {
    id: "contact",
    label: "Contact",
    icon: "mail",
  },
  location: {
    id: "location",
    label: "Localisation",
    icon: "map-pin",
  },
  report: {
    id: "report",
    label: "Compte-rendu",
    disabledLabel: "À remplir à la fin de l’événement",
    disabled: true,
    icon: "image",
  },
};
const StyledMenuItem = styled.button`
  display: flex;
  width: 100%;
  flex-flow: row nowrap;
  align-items: center;
  background-color: transparent;
  text-align: left;
  border: none;
  margin: 0;
  padding: 0;
  font-size: 1rem;
  line-height: 1.1;
  font-weight: 500;
  color: ${({ disabled }) => (disabled ? style.black500 : style.black1000)};
  cursor: ${({ disabled }) => (disabled ? "default" : "pointer")};

  & > * {
    margin: 0;
    padding: 0;
  }

  span {
    flex: 1 1 auto;
  }

  small {
    font-size: 0.75rem;
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: ${({ disabled }) =>
      disabled ? style.black100 : style.secondary500};
    margin-right: 1rem;
    clip-path: circle(1rem);
    text-align: center;
  }
`;

const StyledMenu = styled.div`
  padding: 1.5rem;

  h4 {
    font-weight: 700;
    font-size: 1.25rem;
    line-height: 1.51;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      padding: 0.5rem 0;
    }

    hr {
      border-color: ${style.black200};
      margin: 0.5rem 0;
    }
  }
`;

const ManagementMenuItem = (props) => {
  const { event, item, onClick } = props;

  const handleClick = useCallback(() => {
    onClick && onClick(item);
  }, [item, onClick]);

  const disabled = useMemo(
    () =>
      typeof item.disabled === "function"
        ? item.disabled(event)
        : !!item.disabled,
    [event, item]
  );

  const label = useMemo(
    () => (typeof item.label === "function" ? item.label(event) : item.label),
    [event, item]
  );

  return (
    <StyledMenuItem onClick={handleClick} disabled={disabled}>
      <RawFeatherIcon width="1rem" height="1rem" name={item.icon} />
      <span>
        {label}
        <br />
        {disabled && item.disabledLabel ? (
          <small>{item.disabledLabel}</small>
        ) : null}
      </span>
    </StyledMenuItem>
  );
};
ManagementMenuItem.propTypes = {
  event: PropTypes.object,
  item: PropTypes.shape({
    id: PropTypes.string,
    label: PropTypes.oneOfType([PropTypes.func, PropTypes.bool]),
    disabledLabel: PropTypes.string,
    icon: PropTypes.string,
    disabled: PropTypes.oneOfType([PropTypes.func, PropTypes.bool]),
  }),
  onClick: PropTypes.func,
};

const ManagementMenu = (props) => {
  const { event = events[0], items = MENU_ITEMS, onClick } = props;

  return (
    <StyledMenu>
      <h4>Cortège France insoumise à la marche contre la fourrure 2020</h4>
      <ul>
        {Object.values(items)
          .slice(0, 4)
          .map((item) => (
            <li key={item.id}>
              <ManagementMenuItem event={event} item={item} onClick={onClick} />
            </li>
          ))}
        <hr />
        {Object.values(MENU_ITEMS)
          .slice(4)
          .map((item) => (
            <li key={item.id}>
              <ManagementMenuItem event={event} item={item} onClick={onClick} />
            </li>
          ))}
      </ul>
    </StyledMenu>
  );
};
ManagementMenu.propTypes = {
  event: PropTypes.object,
  items: PropTypes.arrayOf(ManagementMenuItem.item),
  onClick: PropTypes.func.isRequired,
};

export default ManagementMenu;
