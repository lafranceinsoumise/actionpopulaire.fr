import React from "react";
import { useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const Tab = styled.li`
  text-transform: uppercase;
  display: block;
  padding: 0 5px 12px;
  margin: 0 16px -1px 0;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  height: 100%;

  color: ${({ active }) => (active ? style.primary500 : style.black500)};
  border-bottom: ${({ active }) =>
    active ? `3px solid ${style.primary500}` : "3px solid transparent"};

  &:last-child {
    margin-right: 0;
  }

  @media (max-width: ${style.collapse}px) {
    text-align: center;
  }
`;

const TabList = styled.ul`
  padding: 0;
  display: flex;
  width: 100%;
  height: 100%;
  flex-direction: row;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
`;

const TabListWrapper = styled.div`
  position: relative;
  width: 100%;
  height: 22px;
  padding: 0;
  border-bottom: 1px solid ${style.black100};

  @media (max-width: ${style.collapse}px) {
    padding-right: 5%;
    width: calc(100% - 50px);
    margin: 0 auto;
  }

  :before {
    content: "";
    width: 100%;
    height: 100%;
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent 90%, white);
    pointer-events: none;
  }
`;

const FilterTabs = ({ tabs, onTabChange }) => {
  const [tab, setTab] = useState(0);

  return (
    <TabListWrapper>
      <TabList>
        {tabs.map((label, index) => (
          <Tab
            active={index === tab}
            key={index}
            onClick={() => setTab(index) + onTabChange(index)}
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
  onTabChange: PropTypes.func.isRequired,
};
