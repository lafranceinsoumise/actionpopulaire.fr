import PropTypes from "prop-types";
import React from "react";
import { NavLink } from "react-router-dom";

import styled from "styled-components";

const StyledMenu = styled.nav`
  position: sticky;
  z-index: 2;
  top: ${({ $stickyOffset }) => ($stickyOffset || 0) - 1}px;
  left: 0;
  right: 0;
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
  padding: 0;
  margin: 0 1rem;
  background-color: ${(props) => props.theme.background0};
  box-shadow: inset 0px -1px 0px ${(props) => props.theme.text100};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    justify-content: flex-start;
    margin: 0;
    padding: 0 1rem;
    border-top: 1px solid ${(props) => props.theme.text100};
    box-shadow:
      0px 0px 3px rgba(0, 35, 44, 0.1),
      0px 2px 1px rgba(0, 35, 44, 0.08);
    overflow-x: auto;
    overflow-x: overlay;
    overflow-y: hidden;
  }

  a {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 1 auto;
    padding: 0 1rem;
    background-color: transparent;
    border: none;
    height: 5rem;
    cursor: pointer;
    transition: all 200ms ease-in-out;
    box-shadow: none;
    color: ${(props) => props.theme.text1000};
    white-space: nowrap;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 2.875rem;
      min-width: max-content;
      font-size: 14px;
      font-weight: 500;
      padding: 0 0.75rem;
    }

    &.active,
    &:hover,
    &:focus {
      color: ${(props) => props.theme.primary500};
      border: none;
      outline: none;
      text-decoration: none;
    }

    &.active {
      background-size: 100%;
      box-shadow: 0 -3px 0 ${(props) => props.theme.primary500} inset;
    }
  }
`;

const GroupPageMenu = (props) => {
  const { hasTabs, tabs, stickyOffset, activeTabId } = props;

  return hasTabs ? (
    <StyledMenu $stickyOffset={stickyOffset}>
      {tabs.map(
        (tab) =>
          tab.hasTab && (
            <NavLink
              key={tab.id}
              to={tab.getLink()}
              isActive={() => tab.id === activeTabId}
            >
              {tab.label}
            </NavLink>
          ),
      )}
    </StyledMenu>
  ) : null;
};
GroupPageMenu.propTypes = {
  hasTabs: PropTypes.bool,
  tabs: PropTypes.arrayOf(PropTypes.object),
  stickyOffset: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  activeTabId: PropTypes.string,
};
export default GroupPageMenu;
