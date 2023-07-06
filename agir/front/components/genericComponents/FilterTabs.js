import PropTypes from "prop-types";
import React, { useState } from "react";
import { useScrollbarWidth } from "react-use";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const Tab = styled.button`
  background-color: transparent;
  border: none;
  color: ${({ $active }) => ($active ? style.primary500 : style.black500)};
  box-shadow: ${({ $active }) =>
    $active ? `inset 0 -3px 0 ${style.primary500}` : "inset 0 0 0 transparent"};
  transition: all 200ms ease-in-out;
`;

const TabList = styled.div``;

const TabListWrapper = styled.div`
  width: 100%;
  padding: 0;
  overflow-x: auto;
  overflow-y: visible;

  @media (max-width: ${style.collapse}px) {
    margin: 0 auto;
    padding: 0 0 ${(props) => props.$sbw || 16}px;
  }

  ${TabList} {
    padding: 1px 1rem 0 1px;
    white-space: nowrap;
    border-bottom: 1px solid ${style.black200};
    display: inline-flex;
    gap: 16px;
    min-width: 100%;

    ${Tab} {
      display: inline-flex;
      align-items: center;
      justify-content: flex-start;
      width: auto;
      height: 1.5rem;
      text-transform: uppercase;
      padding: 0 2px;
      font-size: 11px;
      font-weight: 600;
      text-align: left;
      cursor: pointer;
      white-space: nowrap;
    }
  }

  &:before {
    content: "";
    width: 100%;
    height: 2rem;
    position: absolute;
    right: 0;
    background: rgba(250, 250, 250, 0.001);
    background-image: -webkit-linear-gradient(
      left,
      rgba(250, 250, 250, 0.001) calc(100% - 3rem),
      rgba(250, 250, 250, 1)
    );
    background-image: linear-gradient(
      to right,
      rgba(250, 250, 250, 0.001) calc(100% - 3rem),
      rgba(250, 250, 250, 1)
    );
    pointer-events: none;
  }
`;

const FilterTabs = (props) => {
  const { tabs, activeTab = 0, onTabChange } = props;

  const sbw = useScrollbarWidth();

  if (tabs.length === 0) {
    return null;
  }

  return (
    <TabListWrapper $sbw={sbw}>
      <TabList>
        {tabs.map((label, index) => (
          <Tab
            key={index}
            $active={index === activeTab}
            onClick={(e) => onTabChange(index)}
          >
            {label}
          </Tab>
        ))}
      </TabList>
    </TabListWrapper>
  );
};

export default FilterTabs;

FilterTabs.propTypes = {
  tabs: PropTypes.arrayOf(PropTypes.string).isRequired,
  activeTab: PropTypes.number,
  onTabChange: PropTypes.func.isRequired,
};
