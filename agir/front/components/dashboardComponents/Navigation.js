import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import FeatherIcon, {
  RawFeatherIcon,
} from "@agir/front/genericComponents/FeatherIcon";
import style from "@agir/front/genericComponents/_variables.scss";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";

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
  margin-top: 40px;
  display: flex;
  flex-flow: column nowrap;
  list-style: none;

  @media only screen and (max-width: ${style.collapse}px) {
    display: none;
  }
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

  & a {
    color: inherit;
    text-decoration: none;
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
  z-index: 1000;
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

const MenuLink = (props) => {
  const {
    href,
    icon,
    title,
    active,
    counter,
    external,
    secondaryLinks,
  } = props;
  const linkProps = React.useMemo(
    () => ({
      target: external ? "_blank" : undefined,
      rel: external ? "noopener noreferrer" : undefined,
    }),
    [external]
  );
  if (counter === 0) {
    return null;
  }
  return (
    <MenuItem {...props} active={active}>
      <a {...linkProps} href={href}>
        {counter > 0 && <Counter>{counter}</Counter>}
        <FeatherIcon name={icon} inline />
        <span>{title}</span>
        {external && <FeatherIcon name="external-link" inline small />}
      </a>
      {Array.isArray(secondaryLinks) && secondaryLinks.length > 0 ? (
        <SecondaryMenu>
          {secondaryLinks.map((link) => (
            <SecondaryMenuItem key={link.id}>
              <a href={link.href}>{link.label}</a>
            </SecondaryMenuItem>
          ))}
        </SecondaryMenu>
      ) : null}
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
  secondaryLinks: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      label: PropTypes.string,
      href: PropTypes.string,
    })
  ),
};

const Navigation = ({ active }) => {
  const { requiredActionActivities = [], routes } = useGlobalContext();
  return (
    <BottomBar>
      <Menu>
        {CONFIG.menuLinks.map((link) => (
          <MenuLink
            {...link}
            key={link.id}
            active={active === link.id}
            href={link.href || routes[link.route]}
            counter={link.counter && requiredActionActivities.length}
            secondaryLinks={link.secondaryLinks && routes[link.secondaryLinks]}
          />
        ))}
      </Menu>
      <SecondaryMenu style={{ padding: 0 }}>
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
    </BottomBar>
  );
};

export default Navigation;

Navigation.propTypes = {
  active: PropTypes.oneOf([
    "events",
    "groups",
    "activity",
    "required-activity",
    "menu",
  ]),
};
