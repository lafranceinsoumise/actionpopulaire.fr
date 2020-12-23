import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Layout from "@agir/front/dashboardComponents/Layout";
import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";

import style from "@agir/front/genericComponents/_variables.scss";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getRequiredActionActivityCount,
  getRoutes,
} from "@agir/front/globalContext/reducers";

import Link from "@agir/front/app/Link";

import { routeConfig } from "@agir/front/app/routes.config";
import CONFIG from "@agir/front/dashboardComponents/navigation.config";

const MAIN_LINKS = CONFIG.menuLinks.filter(({ mobile }) => mobile === false);

const Navigation = styled.nav`
  margin-top: 20px;

  @media only screen and (min-width: ${style.collapse}px) {
    display: none;
  }
`;

const Menu = styled.ul`
  display: flex;
  flex-flow: column nowrap;
`;

const MenuItem = styled.li`
  font-size: 16px;
  font-weight: 600;
  display: block;
  position: relative;
  line-height: 24px;
  align-items: center;
  margin-bottom: 1rem;

  & ${RawFeatherIcon} {
    color: ${(props) => (props.active ? style.primary500 : style.black500)};
    margin-right: 1rem;
  }

  ${RawFeatherIcon}:last-child {
    margin-right: 0;
    margin-left: 0.5rem;
  }

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

const MenuLink = (props) => {
  const { href, to, icon, title, active, counter, external } = props;
  return (
    <MenuItem {...props} active={active}>
      <Link href={href} to={to}>
        {counter > 0 && <Counter>{counter}</Counter>}
        <FeatherIcon name={icon} inline />
        <span>{title}</span>
        {external && <FeatherIcon name="external-link" inline small />}
      </Link>
    </MenuItem>
  );
};
MenuLink.propTypes = {
  href: PropTypes.string,
  to: PropTypes.string,
  icon: PropTypes.string,
  title: PropTypes.string,
  active: PropTypes.bool,
  counter: PropTypes.number,
  external: PropTypes.bool,
};

const NavigationPage = ({ active }) => {
  const requiredActionActivityCount = useSelector(
    getRequiredActionActivityCount
  );
  const routes = useSelector(getRoutes);
  return (
    <Layout active="menu" desktopOnlyFooter={false}>
      <Navigation>
        <Menu>
          {MAIN_LINKS.map((link) =>
            link.href || routes[link.route] ? (
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
                counter={link.counter && requiredActionActivityCount}
              />
            ) : null
          )}
        </Menu>
      </Navigation>
    </Layout>
  );
};

export default NavigationPage;

NavigationPage.propTypes = {
  active: PropTypes.oneOf(["events", "groups", "activity", "menu"]),
};
