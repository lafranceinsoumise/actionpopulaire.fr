import React from "react";
import { useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import styles from "@agir/front/genericComponents/_variables.scss";

const Tab = styled.li`
  text-transform: uppercase;
  display: block;
  padding: 0 0px 12px;
  margin: 0 16px -1px 0;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;

  color: ${({ active }) => (active ? styles.primary500 : styles.black500)};
  ${({ active }) => active && `border-bottom: 2px solid ${styles.primary500}`}
`;

const TabList = styled.ul`
  padding: 0;
  display: inline-flex;
  max-width: 100%;
  flex-direction: horizontal;
  overflow: hidden visible;
  border-bottom: 1px solid ${styles.black100};
  & > ${Tab}:last-child {
    margin-right: 0;
  }

  &:after {
    content: " ";
    position: absolute;
    height: 100%;
    width: 100%;
    pointer-events: none;
    background: linear-gradient(
      90deg,
      rgba(0, 0, 0, 0) 76%,
      rgba(255, 255, 255, 1) 97%
    );
  }
`;

const FilterTabs = ({ tabs, onTabChange }) => {
  const [tab, setTab] = useState(0);

  return (
    <TabList>
      {tabs.map((label, index) => (
        <Tab
          active={index === tab}
          key={index}
          onClick={() =>
            setTab(index) &&
            typeof onTabChange === "function" &&
            onTabChange(index)
          }
        >
          {label}
        </Tab>
      ))}
    </TabList>
  );
};

export default FilterTabs;

FilterTabs.propTypes = {
  tabs: PropTypes.arrayOf(PropTypes.string),
};
