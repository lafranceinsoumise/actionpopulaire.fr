import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";

import style from "@agir/front/genericComponents/_variables.scss";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

import Link from "@agir/front/app/Link";

import { routeConfig } from "@agir/front/app/routes.config";
import CONFIG from "@agir/front/dashboardComponents/navigation.config";

import { useUnreadMessageCount } from "@agir/msgs/common/hooks";
import { useUnreadActivityCount } from "@agir/activity/common/hooks";

const BottomBar = styled.nav`
  @media only screen and (max-width: ${style.collapse}px) {
    background-color: ${style.white};
    position: fixed;
    bottom: 0px;
    left: 0px;
    right: 0px;
    box-shadow: inset 0px 1px 0px #eeeeee;
    height: 72px;
    padding: 0 0.5rem;
    z-index: ${style.zindexBottomBar};
    isolation: isolate;
  }
`;

const SecondaryMenu = styled.ul`
  margin-top: 1.5rem;
  display: flex;
  flex-flow: column nowrap;
  list-style: none;
  max-width: 100%;

  &:first-child {
    margin-top: 0;
  }

  @media only screen and (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const SecondaryMenuItem = styled.li`
  font-size: 12px;
  line-height: 15px;
  color: ${style.black500};
  margin-bottom: 12px;
  font-weight: bold;
  overflow-wrap: break-word;

  & a,
  & a:hover,
  & a:focus,
  & a:active {
    font-size: 13px;
    font-weight: normal;
    line-height: 1.1;
    color: ${style.black700};
    margin-bottom: 12px;
  }
`;

const Menu = styled.ul`
  padding: 0;

  @media only screen and (max-width: ${style.collapse}px) {
    max-width: 600px;
    margin: auto;
    display: flex;
    justify-content: space-around;
  }
`;

const MenuItem = styled.li`
  font-size: 16px;
  font-weight: 600;
  display: block;
  position: relative;
  color: ${(props) => (props.active ? style.primary500 : "")};

  @media only screen and (max-width: ${style.collapse}px) {
    flex: 1 1 auto;
    display: ${({ mobile }) => (mobile ? "flex" : "none")};
    max-width: 70px;
    height: 70px;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    font-size: 11px;
    font-weight: 500;
    border-top: 2px solid
      ${(props) => (props.active ? style.primary500 : "transparent")};

    & ${RawFeatherIcon} {
      display: block;
      margin-bottom: 5px;
    }
  }

  @media only screen and (min-width: ${style.collapse}px) {
    display: ${({ desktop }) => (desktop ? "flex" : "none")};
    line-height: 24px;
    align-items: center;
    margin-bottom: 1rem;
    flex-flow: column nowrap;
    align-items: flex-start;

    & ${RawFeatherIcon} {
      color: ${(props) => (props.active ? style.primary500 : style.black500)};
      margin-right: 1rem;
    }

    & ${RawFeatherIcon}:last-child {
      margin-right: 0;
      margin-left: 0.5rem;
    }

    & ${SecondaryMenu} {
      margin-top: 12px;
      margin-bottom: 0;

      ${SecondaryMenuItem} {
        font-weight: 500;
        color: #333333;
        margin-bottom: 12px;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }

  & a {
    color: inherit;
    text-decoration: none;
  }

  & ${RawFeatherIcon} {
    position: relative;

    &::after {
      content: "";
      display: block;
      position: absolute;
      width: 6px;
      height: 6px;
      border-radius: 100%;
      background-color: ${({ hasUnreadBadge }) =>
        hasUnreadBadge ? "crimson" : "transparent"};

      @media only screen and (max-width: ${style.collapse}px) {
        top: 3px;
        right: 20px;
      }

      @media only screen and (min-width: ${style.collapse}px) {
        top: 3px;
        right: -3px;
      }
    }
  }
`;

const Counter = styled.span`
  position: absolute;
  background-color: ${style.redNSP};
  color: #fff;
  font-size: 9px;
  height: 16px;
  width: 16px;
  border-radius: ${style.borderRadius};
  z-index: ${style.zindexNavigationCounter};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-variant-numeric: tabular-nums;

  @media only screen and (max-width: ${style.collapse}px) {
    top: 11px;
    right: 50%;
    transform: translateX(calc(12px + 50%));
  }

  @media only screen and (max-width: 360px) {
    top: 16px;
  }

  @media only screen and (min-width: ${style.collapse}px) {
    top: 0px;
    left: 14px;
  }
`;

const Title = styled.span`
  @media (max-width: 360px) {
    font-size: 0.563rem;
  }
  @media (max-width: 340px) {
    display: none;
  }
`;

const MenuLink = (props) => {
  const {
    href,
    to,
    icon,
    title,
    active,
    counter,
    hasUnreadBadge,
    external,
    secondaryLinks,
  } = props;
  return (
    <MenuItem {...props} active={active} hasUnreadBadge={hasUnreadBadge}>
      <Link href={href} to={to}>
        {counter > 0 && <Counter>{counter}</Counter>}
        <FeatherIcon name={icon} inline />
        <Title>{title}</Title>
        {external && <FeatherIcon name="external-link" inline small />}
      </Link>
      {Array.isArray(secondaryLinks) && secondaryLinks.length > 0 ? (
        <SecondaryMenu>
          {secondaryLinks.map((link) => (
            <SecondaryMenuItem key={link.id}>
              <Link
                href={link.href}
                to={
                  link.to && routeConfig[link.to]
                    ? routeConfig[link.to].getLink()
                    : link.to || undefined
                }
              >
                {link.label}
              </Link>
            </SecondaryMenuItem>
          ))}
        </SecondaryMenu>
      ) : null}
    </MenuItem>
  );
};
MenuLink.propTypes = {
  id: PropTypes.string,
  href: PropTypes.string,
  to: PropTypes.string,
  icon: PropTypes.string,
  title: PropTypes.string,
  active: PropTypes.bool,
  counter: PropTypes.number,
  hasUnreadBadge: PropTypes.bool,
  external: PropTypes.bool,
  secondaryLinks: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      label: PropTypes.string,
      href: PropTypes.string,
    })
  ),
};

const Navigation = ({ active }) => {
  const unreadActivityCount = useUnreadActivityCount();
  const unreadMessageCount = useUnreadMessageCount();
  const routes = useSelector(getRoutes);

  return (
    <BottomBar>
      <Menu>
        {CONFIG.menuLinks.map(
          (link) =>
            (link.href || routes[link.route] || link.to) && (
              <MenuLink
                {...link}
                key={link.id}
                active={active === link.id}
                href={link.href || routes[link.route]}
                to={
                  link.to && routeConfig[link.to]
                    ? routeConfig[link.to].getLink()
                    : undefined
                }
                counter={
                  link.unreadMessageCounter
                    ? unreadMessageCount
                    : link.unreadActivityBadge
                    ? unreadActivityCount
                    : undefined
                }
                secondaryLinks={
                  link.secondaryLinks && routes[link.secondaryLinks]
                }
              />
            )
        )}
      </Menu>
    </BottomBar>
  );
};

export const SecondaryNavigation = () => {
  const routes = useSelector(getRoutes);
  return (
    <SecondaryMenu style={{ padding: 0 }}>
      <SecondaryMenuItem key="title">LIENS</SecondaryMenuItem>
      {CONFIG.secondaryLinks.map(
        (link) =>
          (link.href || routes[link.route] || routeConfig[link.to]) && (
            <SecondaryMenuItem key={link.id}>
              <Link
                href={link.href || routes[link.route]}
                to={
                  link.to && routeConfig[link.to]
                    ? routeConfig[link.to].getLink()
                    : undefined
                }
              >
                {link.title}
              </Link>
            </SecondaryMenuItem>
          )
      )}
    </SecondaryMenu>
  );
};

export default Navigation;

Navigation.propTypes = {
  active: PropTypes.string,
};
