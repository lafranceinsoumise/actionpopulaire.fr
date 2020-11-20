import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Layout from "@agir/front/dashboardComponents/Layout";
import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";

import style from "@agir/front/genericComponents/_variables.scss";
import { useGlobalContext } from "@agir/front/genericComponents/GobalContext";

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
  margin-bottom: 1.5rem;

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

const SecondaryMenu = styled.ul`
  margin-top: 40px;
  display: flex;
  flex-flow: column nowrap;
  list-style: none;
`;

const SecondaryMenuItem = styled.li`
  font-size: 12px;
  line-height: 15px;
  color: ${style.black500};
  margin-bottom: 16px;
  font-weight: bold;

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

const Counter = styled.span`
  text-align: center;
  position: absolute;
  background-color: ${style.secondary500};
  color: #fff;
  font-size: 9px;
  height: 16px;
  width: 16px;
  border-radius: 8px;
  z-index: 1000;
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
  const { href, icon, title, active, counter, external } = props;
  const linkProps = React.useMemo(
    () => ({
      target: external ? "_blank" : undefined,
      rel: external ? "noopener noreferrer" : undefined,
    }),
    [external]
  );
  return (
    <MenuItem {...props} active={active}>
      <a {...linkProps} href={href}>
        {counter > 0 && <Counter>{counter}</Counter>}
        <FeatherIcon name={icon} inline />
        <span>{title}</span>
        {external && <FeatherIcon name="external-link" inline small />}
      </a>
    </MenuItem>
  );
};
MenuLink.propTypes = {
  href: PropTypes.string,
  icon: PropTypes.string,
  title: PropTypes.string,
  active: PropTypes.bool,
  counter: PropTypes.number,
  external: PropTypes.bool,
};

const NavigationPage = ({ active }) => {
  const { requiredActionActivities = [], routes } = useGlobalContext();
  return (
    <Layout active="menu">
      <Navigation>
        <Menu>
          {MAIN_LINKS.map((link) => (
            <MenuLink
              {...link}
              key={link.id}
              active={active === link.id}
              href={link.href || routes[link.route]}
              counter={link.counter && requiredActionActivities.length}
            />
          ))}
        </Menu>
        <SecondaryMenu>
          <SecondaryMenuItem key="title">LIENS</SecondaryMenuItem>
          {CONFIG.secondaryLinks.map((link) => (
            <SecondaryMenuItem key={link.id}>
              <a
                href={link.href || routes[link.route]}
                target="_blank"
                rel="noopener noreferrer"
              >
                {link.title}
              </a>
            </SecondaryMenuItem>
          ))}
        </SecondaryMenu>
      </Navigation>
    </Layout>
  );
};

export default NavigationPage;

NavigationPage.propTypes = {
  active: PropTypes.oneOf(["events", "groups", "activity", "menu"]),
};
