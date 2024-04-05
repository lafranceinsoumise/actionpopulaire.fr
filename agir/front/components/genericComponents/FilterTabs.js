import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { useScrollbarWidth } from "react-use";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

const Tab = styled.button`
  background-color: transparent;
  border: none;
  color: ${({ $active }) => ($active ? style.primary500 : style.black500)};
  box-shadow: ${({ $active }) =>
    $active
      ? `inset 0 -0.1875rem 0 ${style.primary500}`
      : "inset 0 0 0 transparent"};
  transition: all 200ms ease-in-out;

  &:disabled {
    color: ${style.black200};
  }
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
    padding: 0.0625rem 1rem 0 0.0625rem;
    white-space: nowrap;
    border-bottom: 0.0625rem solid ${style.black200};
    display: inline-flex;
    gap: 1rem;
    min-width: 100%;

    ${Tab} {
      display: inline-flex;
      align-items: center;
      justify-content: flex-start;
      width: auto;
      height: ${(props) => (props.$small ? "1.5rem" : "2rem")};
      text-transform: uppercase;
      padding: 0 0.125rem;
      font-size: ${(props) => (props.$small ? ".6875rem" : "0.875rem")};
      font-weight: 600;
      text-align: left;
      cursor: pointer;
      white-space: nowrap;

      &:disabled {
        cursor: default;
      }
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
  const { tabs, activeTab = 0, onTabChange, small = true, ...rest } = props;

  const sbw = useScrollbarWidth();

  const tabConfigs = useMemo(() => {
    if (!Array.isArray(tabs)) {
      return tabs;
    }

    return tabs.map((tab) => (typeof tab === "string" ? { label: tab } : tab));
  }, [tabs]);

  if (tabConfigs.length === 0) {
    return null;
  }

  return (
    <TabListWrapper {...rest} $sbw={sbw} $small={small}>
      <TabList>
        {tabConfigs.map((tabConfig, index) => (
          <Tab
            {...tabConfig}
            key={index}
            $active={index === activeTab}
            onClick={() => onTabChange(index)}
          >
            {tabConfig.label}
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
  small: PropTypes.bool,
};
