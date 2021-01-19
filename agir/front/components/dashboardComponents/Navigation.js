import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";
import Tooltip from "@agir/front/genericComponents/Tooltip";

import style from "@agir/front/genericComponents/_variables.scss";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getRoutes,
  getUnreadActivitiesCount,
  getRequiredActionActivityCount,
  getUser,
} from "@agir/front/globalContext/reducers";

import Link from "@agir/front/app/Link";

import { routeConfig } from "@agir/front/app/routes.config";
import CONFIG from "@agir/front/dashboardComponents/navigation.config";

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

const MenuItemTooltip = styled.div`
  @media only screen and (min-width: ${style.collapse}px) {
    display: none;
  }
`;

const MenuItem = styled.li`
  font-size: 16px;
  font-weight: 600;
  display: block;
  position: relative;
  color: ${(props) => (props.active ? style.primary500 : "")};

  & a {
    color: inherit;
    text-decoration: none;
  }

  & ${MenuItemTooltip} + a {
    &::after {
      content: "";
      display: block;
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      bottom: 0;
      border-radius: 100%;
      background-image: radial-gradient(
        rgba(255, 255, 255, 0.001) calc(100% - 28px),
        ${style.primary500} calc(100% - 27px),
        ${style.primary500} calc(100% - 26px),
        rgba(107, 46, 255, 0.2) calc(100% - 25px),
        rgba(107, 46, 255, 0.2) 100%
      );
      transform-origin: center center;
      pointer-events: none;
      transition: all 200ms ease-in;
      transform: scale3d(1.2, 1.2, 1);
      opacity: 0;
    }
  }

  & ${MenuItemTooltip}.active + a {
    &::after {
      opacity: 1;
      transform: scale3d(1.65, 1.65, 1);
    }
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
        right: 16px;
      }

      @media only screen and (min-width: ${style.collapse}px) {
        top: 3px;
        right: -6px;
      }
    }
  }

  @media only screen and (max-width: ${style.collapse}px) {
    display: ${({ mobile }) => (mobile ? "flex" : "none")};
    width: 70px;
    height: 70px;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    font-size: 11px;
    font-weight: 500;
    border-top: 2px solid
      ${(props) => (props.active ? style.primary500 : "transparent")};

    & .large-only {
      display: none;
    }

    & ${RawFeatherIcon} {
      display: block;
      margin-bottom: 5px;
    }
  }

  @media only screen and (max-width: 340px) {
    font-size: 9px;
  }

  @media only screen and (min-width: ${style.collapse}px) {
    display: ${({ desktop }) => (desktop ? "flex" : "none")};
    line-height: 24px;
    align-items: center;
    margin-bottom: 1rem;
    flex-flow: column nowrap;
    align-items: flex-start;

    & .small-only {
      display: none;
    }

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
`;

const Counter = styled.span`
  position: absolute;
  background-color: ${style.redNSP};
  color: #fff;
  font-size: 9px;
  height: 16px;
  width: 16px;
  border-radius: 8px;
  z-index: ${style.zindexNavigationCounter};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-variant-numeric: tabular-nums;

  @media only screen and (max-width: ${style.collapse}px) {
    top: 11px;
    right: 16px;
  }

  @media only screen and (min-width: ${style.collapse}px) {
    top: 0px;
    left: 14px;
  }
`;

const TooltipGroups = () => {
  const user = useSelector(getUser);
  const [shouldShow, setShouldShow] = React.useState(false);
  const handleClose = React.useCallback(() => setShouldShow(false), []);

  React.useEffect(() => {
    if (!!user && user.isAgir && user.isGroupManager) {
      const shouldHide = window.localStorage.getItem("AP_menu-groups-tooltip");
      if (shouldHide) {
        return;
      }
      window.localStorage.setItem("AP_menu-groups-tooltip", "1");
      setShouldShow(true);
    }
  }, [user]);

  return (
    <MenuItemTooltip className={`small-only ${shouldShow ? "active" : ""}`}>
      <Tooltip position="top-center" shouldShow={shouldShow}>
        <p>Retrouvez vos GA dans l'onglet "Groupes"</p>
        <p>
          <Button color="secondary" small onClick={handleClose}>
            Merci !
          </Button>
        </p>
      </Tooltip>
    </MenuItemTooltip>
  );
};

const Tooltips = {
  groups: TooltipGroups,
};

const MenuLink = (props) => {
  const {
    id,
    href,
    to,
    icon,
    title,
    shortTitle,
    active,
    counter,
    hasUnreadBadge,
    external,
    secondaryLinks,
  } = props;
  const ItemTooltip = React.useMemo(() => Tooltips[id], [id]);
  return (
    <MenuItem {...props} active={active} hasUnreadBadge={hasUnreadBadge}>
      {ItemTooltip ? <ItemTooltip /> : null}
      <Link href={href} to={to}>
        {counter > 0 && <Counter>{counter}</Counter>}
        <FeatherIcon name={icon} inline />
        <span className="small-only">{shortTitle || title}</span>
        <span className="large-only">{title}</span>
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
                    ? routeConfig[link.to].pathname
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
  shortTitle: PropTypes.string,
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
  const requiredActionActivityCount = useSelector(
    getRequiredActionActivityCount
  );
  const unreadActivityCount = useSelector(getUnreadActivitiesCount);
  const routes = useSelector(getRoutes);

  return (
    <BottomBar>
      <Menu>
        {CONFIG.menuLinks.map((link) =>
          link.href || routes[link.route] || link.to ? (
            <MenuLink
              {...link}
              key={link.id}
              active={active === link.id}
              href={link.href || routes[link.route]}
              to={
                link.to && routeConfig[link.to]
                  ? routeConfig[link.to].pathname
                  : undefined
              }
              counter={
                link.requiredActivityCounter && requiredActionActivityCount
              }
              hasUnreadBadge={
                !!link.unreadActivityBadge && unreadActivityCount > 0
              }
              secondaryLinks={
                link.secondaryLinks && routes[link.secondaryLinks]
              }
            />
          ) : null
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
      {CONFIG.secondaryLinks.map((link) =>
        link.href || routes[link.route] ? (
          <SecondaryMenuItem key={link.id}>
            <Link
              href={link.href || routes[link.route]}
              to={
                link.to && routeConfig[link.to]
                  ? routeConfig[link.to].pathname
                  : undefined
              }
            >
              {link.title}
            </Link>
          </SecondaryMenuItem>
        ) : null
      )}
    </SecondaryMenu>
  );
};

export default Navigation;

Navigation.propTypes = {
  active: PropTypes.string,
};
