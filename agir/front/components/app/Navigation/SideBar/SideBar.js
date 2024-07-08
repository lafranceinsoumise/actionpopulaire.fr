import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import CONFIG from "@agir/front/app/Navigation/navigation.config";

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
  color: ${({ $active, theme }) => ($active ? theme.primary500 : "inherit")};

  &:hover,
  &:focus {
    color: ${({ $active, theme }) => ($active ? theme.primary500 : "inherit")};
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
    color: ${({ $active, theme }) =>
      $active ? theme.primary500 : theme.text500};
    margin-right: 1rem;
  }

  ${RawFeatherIcon}:last-child {
    align-self: baseline;
    margin-right: 0;
    margin-left: 0.5rem;
  }
`;

const LINKS = CONFIG.menuLinks.filter(({ desktop }) => !!desktop);

const NavigationLink = ({
  link,
  active,
  routes,
  unreadMessageCount = 0,
  unreadActivityCount = 0,
}) => {
  const secondaryLinks = useMemo(() => {
    if (!routes) {
      return null;
    }
    if (Array.isArray(link.secondaryLinks)) {
      return link.secondaryLinks;
    }

    return routes[link.secondaryLinks];
  }, [routes, link.secondaryLinks]);

  return (
    <li style={{ marginBottom: "1.5rem" }}>
      <MenuLink route={link.route} $active={active === link.id}>
        {link.unreadMessageBadge && <CounterBadge value={unreadMessageCount} />}
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
      <SecondaryMenu style={{ marginTop: ".5rem" }} links={secondaryLinks} />
    </li>
  );
};

const Navigation = (props) => {
  return (
    <ul style={{ listStyle: "none", padding: 0 }}>
      {LINKS.map((link) => (
        <NavigationLink key={link.id} {...props} link={link} />
      ))}
    </ul>
  );
};

Navigation.propTypes = {
  active: PropTypes.string,
  unreadActivityCount: PropTypes.number,
  unreadMessageCount: PropTypes.number,
  routes: PropTypes.object,
};
export default Navigation;
