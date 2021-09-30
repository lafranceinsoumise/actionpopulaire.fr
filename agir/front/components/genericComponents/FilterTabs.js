import React from "react";
import { useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const Tab = styled.li`
  text-transform: uppercase;
  display: block;
  padding: 0;
  margin: 0 0 -1px 16px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  height: 100%;

  color: ${({ active }) => (active ? style.primary500 : style.black500)};
  border-bottom: ${({ active }) =>
    active ? `3px solid ${style.primary500}` : "3px solid transparent"};

  &:first-child {
    margin-left: 0;
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

  &:after {
    content: "";
    display: block;
    padding-right: 1.5rem;
    height: 100%;
  }
`;

const TabListWrapper = styled.div`
  position: relative;
  width: 100%;
  height: 24px;
  padding: 0;
  border-bottom: 1px solid ${style.black100};

  @media (max-width: ${style.collapse}px) {
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
    background: rgba(250, 250, 250, 0.001);
    background-image: -webkit-linear-gradient(
      left,
      rgba(250, 250, 250, 0.001) calc(100% - 2rem),
      rgba(250, 250, 250, 1)
    );
    background-image: linear-gradient(
      to right,
      rgba(250, 250, 250, 0.001) calc(100% - 2rem),
      rgba(250, 250, 250, 1)
    );
    pointer-events: none;
  }
`;

const FilterTabs = ({ tabs, onTabChange, style }) => {
  const [tab, setTab] = useState(0);

  if (tabs.length === 0) {
    return null;
  }

  return (
    <TabListWrapper style={style}>
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
  style: PropTypes.object,
};
