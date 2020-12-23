import styled from "styled-components";
import React from "react";
import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";
import style from "@agir/front/genericComponents/_variables.scss";
import PropTypes from "prop-types";

const BottomBar = styled.nav`
  @media only screen and (max-width: ${style.collapse}px) {
    position: absolute;
    bottom: 0px;
    left: 0px;
    right: 0px;
    box-shadow: inset 0px 1px 0px #eeeeee;
    height: 72px;
    padding: 0 7%;
  }
`;

const Menu = styled.ul`
  @media only screen and (max-width: ${style.collapse}px) {
    padding: 0;
    max-width: 600px;
    margin: auto;
    display: flex;
    justify-content: space-between;
  }
`;

const MenuItem = styled.li`
  @media only screen and (max-width: ${style.collapse}px) {
    width: 70px;
    height: 70px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    font-size: 11px;

    & ${RawFeatherIcon} {
      display: block;
    }
    ${(props) =>
      props.active &&
      `
    border-top: 2px solid ${style.primary500};
    `}
  }

  @media only screen and (min-width: ${style.collapse}px) {
    margin-bottom: 1.5rem;
    & ${RawFeatherIcon} {
      color: ${(props) => (props.active ? style.primary500 : style.black500)};
      margin-right: 1rem;
    }
  }

  font-size: 16px;
  font-weight: 600;

  display: block;
  position: relative;

  & a {
    color: inherit;
    text-decoration: none;
  }

  ${(props) =>
    props.active &&
    `
    color: ${style.primary500};
    `}
`;

const Counter = styled.span`
  text-align: center;
  position: absolute;
  background-color: ${style.secondary500};
  color: #fff;
  font-size: 9px;
  height: 16px;
  width: 16px;
  border-radius: 8px;
  z-index: ${style.zindexNavigationCounter};
  line-height: 14px;

  @media only screen and (max-width: ${style.collapse}px) {
    top: 11px;
    right: 16px;
  }

  @media only screen and (min-width: ${style.collapse}px) {
    top: 0px;
    left: 14px;
  }
`;

// eslint-disable-next-line react/prop-types
const MenuLink = ({ href, icon, title, active, counter }) => (
  <MenuItem active={active}>
    <a href={href}>
      {counter > 0 && <Counter>{counter}</Counter>}
      <FeatherIcon name={icon} inline />
      <span>{title}</span>
    </a>
  </MenuItem>
);

const Navigation = ({ active, routes }) => (
  <BottomBar>
    <Menu>
      <MenuLink
        active={active === "events"}
        icon="calendar"
        title="Événements"
        href={routes.events}
      />
      <MenuLink
        active={active === "groups"}
        icon="users"
        title="Groupes"
        href={routes.groups}
      />
      <MenuLink
        active={active === "notifications"}
        icon="bell"
        title="Notifications"
        href={routes.notifications}
        counter={2}
      />
      <MenuLink
        active={active === "menu"}
        icon="menu"
        title="Plus"
        href={routes.menu}
      />
    </Menu>
  </BottomBar>
);

export default Navigation;

Navigation.propTypes = {
  active: PropTypes.string,
  routes: PropTypes.shape({
    events: PropTypes.string.isRequired,
    groups: PropTypes.string.isRequired,
    notifications: PropTypes.string.isRequired,
    menu: PropTypes.string.isRequired,
  }),
};
