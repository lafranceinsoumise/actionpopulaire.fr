import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import CONFIG from "@agir/front/app/Navigation/navigation.config";
import * as style from "@agir/front/genericComponents/_variables.scss";

import CounterBadge from "@agir/front/app/Navigation/CounterBadge";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import SecondaryMenu from "./SecondaryMenu";

const MenuLink = styled(Link)`
  position: relative;
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  height: 1.5rem;

  font-size: 1rem;
  line-height: 1.5;
  font-weight: 600;
  color: ${({ $active }) => ($active ? style.primary500 : "inherit")};

  &:hover,
  &:focus {
    color: ${({ $active }) => ($active ? style.primary500 : "inherit")};
    text-decoration: none;
  }

  ${CounterBadge} {
    position: absolute;
    left: 14px;
    top: -5px;
  }

  ${RawFeatherIcon} {
    display: inline-block;
    line-height: 0;
    color: ${({ $active }) => ($active ? style.primary500 : style.black500)};
    margin-right: 1rem;
  }

  ${RawFeatherIcon}:last-child {
    align-self: baseline;
    margin-right: 0;
    margin-left: 0.5rem;
  }
`;

const LINKS = CONFIG.menuLinks.filter(({ desktop }) => !!desktop);

const Navigation = ({
  active,
  unreadMessageCount = 0,
  unreadActivityCount = 0,
  routes,
}) => (
  <ul style={{ listStyle: "none", padding: 0 }}>
    {LINKS.map((link) => (
      <li key={link.id} style={{ marginBottom: "1.5rem" }}>
        <MenuLink route={link.route} $active={active === link.id}>
          {link.unreadMessageBadge && (
            <CounterBadge value={unreadMessageCount} />
          )}
          {link.unreadActivityBadge && (
            <CounterBadge value={unreadActivityCount} />
          )}
          <RawFeatherIcon name={link.icon} />
          <span>{link.title}</span>
          {link.external && (
            <RawFeatherIcon
              name="external-link"
              inline
              strokeWidth={1.33}
              width="1rem"
              height="1rem"
            />
          )}
        </MenuLink>
        <SecondaryMenu
          style={{ marginTop: ".5rem" }}
          links={routes && link.secondaryLinks && routes[link.secondaryLinks]}
        />
      </li>
    ))}
  </ul>
);

Navigation.propTypes = {
  active: PropTypes.string,
  unreadActivityCount: PropTypes.number,
  unreadMessageCount: PropTypes.number,
  routes: PropTypes.object,
};
export default Navigation;
