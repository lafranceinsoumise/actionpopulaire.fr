import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import CONFIG from "@agir/front/app/Navigation/navigation.config";
import * as style from "@agir/front/genericComponents/_variables.scss";

import CounterBadge from "@agir/front/app/Navigation/CounterBadge";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const Title = styled.span``;
const MenuLink = styled(Link)`
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  height: 70px;
  font-size: 11px;
  font-weight: 500;
  color: ${({ $active }) => ($active ? style.primary500 : "inherit")};
  border-top: 2px solid
    ${({ $active }) => ($active ? style.primary500 : "transparent")};

  &:hover,
  &:focus {
    color: ${({ $active }) => ($active ? style.primary500 : "inherit")};
    text-decoration: none;
  }

  ${RawFeatherIcon} {
    display: block;
  }

  ${Title} {
    font-size: 10px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;

    @media (max-width: 340px) {
      font-size: 8px;
    }
  }

  ${CounterBadge} {
    position: absolute;
    top: 7px;
    right: 14px;

    @media (max-width: 340px) {
      top: 9px;
    }
  }
`;

const StyledBottomBar = styled.nav`
  background-color: ${(props) => props.theme.white};
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  box-shadow: inset 0 1px 0 ${(props) => props.theme.black50};
  height: 72px;
  padding: 0 0.5rem;
  z-index: ${(props) => props.theme.zindexBottomBar};
  isolation: isolate;
  overflow: hidden;

  ul {
    padding: 0;
    max-width: 600px;
    margin: auto;
    display: flex;
    justify-content: space-around;
    list-style: none;

    li {
      flex: 1 1 auto;
      max-width: 70px;
      min-width: 1px;
    }
  }
`;

const LINKS = CONFIG.menuLinks.filter(({ mobile }) => !!mobile);

const BottomBar = ({ active, unreadMessageCount, unreadActivityCount }) => (
  <StyledBottomBar>
    <ul>
      {LINKS.map((link) => (
        <li key={link.id}>
          <MenuLink route={link.route} $active={active === link.id}>
            {link.unreadMessageBadge && (
              <CounterBadge value={unreadMessageCount} />
            )}
            {link.unreadActivityBadge && (
              <CounterBadge value={unreadActivityCount} />
            )}
            <RawFeatherIcon name={link.icon} inline />
            <Title>{link.title}</Title>
          </MenuLink>
        </li>
      ))}
    </ul>
  </StyledBottomBar>
);

BottomBar.propTypes = {
  active: PropTypes.string,
  unreadActivityCount: PropTypes.number,
  unreadMessageCount: PropTypes.number,
};
export default BottomBar;
