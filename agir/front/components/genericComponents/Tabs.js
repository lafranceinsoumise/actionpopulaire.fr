import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { useSpring, animated } from "@react-spring/web";
import { useDrag } from "@use-gesture/react";
import styled from "styled-components";

const StyledMenu = styled.nav`
  position: sticky;
  top: ${({ $stickyOffset }) => ($stickyOffset || 0) - 1}px;
  left: 0;
  right: 0;
  display: flex;
  flex-flow: row nowrap;
  padding: 0 1rem;
  background-color: ${(props) => props.theme.background0};
  border-top: 1px solid #dfdfdf;
  box-shadow:
    0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 2px 1px rgba(0, 35, 44, 0.08);
  overflow-x: auto;
  overflow-x: overlay;
  overflow-y: hidden;

  ${({ $noBorder }) =>
    $noBorder &&
    `
    box-shadow: 0px 0px 0px rgba(0, 35, 44, 0.1), 0px 2px 1px rgba(0, 35, 44, 0.08);
    border-top: 0;
  `};

  button {
    flex: 1 1 auto;
    background-color: ${(props) => props.theme.background0};
    border: none;
    height: 2.875rem;
    cursor: pointer;
    transition: all 200ms ease-in-out;
    box-shadow: none;
    color: ${(props) => props.theme.text1000};
    white-space: nowrap;
    min-width: max-content;

    &[data-active],
    &:hover,
    &:focus {
      color: ${(props) => props.theme.primary500};
    }

    &[data-active] {
      background-size: 100%;
      box-shadow: 0 -3px 0 ${(props) => props.theme.primary500} inset;
    }
  }
`;
const StyledContent = styled(animated.div)``;
const StyledTabs = styled.div`
  touch-action: pan-y;
  overflow-x: hidden;
  overflow-y: auto;
`;

const useTabs = (props) => {
  const { tabs, activeTab, activeTabIndex, onTabChange, onNextTab, onPrevTab } =
    props;

  const isControlled =
    !!activeTab &&
    typeof activeTabIndex === "number" &&
    typeof onTabChange === "function";

  const [activeIndex, setActiveIndex] = useState(0);
  const handleClick = useCallback(
    (e) => {
      const index = e.target.dataset.index;
      onTabChange && onTabChange(tabs[index]);
      setActiveIndex(index);
    },
    [tabs, onTabChange, isControlled],
  );

  const handleNext = useCallback(() => {
    if (isControlled) {
      onNextTab();
    } else {
      setActiveIndex((state) => Math.min(state + 1, tabs.length - 1));
    }
  }, [isControlled, onNextTab, tabs.length]);

  const handlePrev = useCallback(() => {
    if (isControlled) {
      onPrevTab();
    } else {
      setActiveIndex((state) => Math.max(0, state - 1));
    }
  }, [isControlled, onPrevTab]);

  const active = useMemo(
    () => tabs[activeIndex] || tabs[0],
    [activeIndex, tabs],
  );

  return {
    active: isControlled ? activeTab : active,
    activeIndex: isControlled ? activeTabIndex : activeIndex,
    handleClick,
    handleNext,
    handlePrev,
  };
};

export const Tabs = (props) => {
  const {
    children,
    tabs,
    stickyOffset,
    activeIndex = 0,
    onTabChange,
    noBorder,
  } = props;

  const active = tabs[activeIndex];

  const ActiveStep = useMemo(() => {
    return (Array.isArray(children) && children[activeIndex]) || null;
  }, [activeIndex, children]);

  const [{ xy }, set] = useSpring(() => ({ xy: [0, 0] }));

  // Set the drag hook and define component movement based on gesture data
  const bind = useDrag(
    ({ args: [limit], down, movement: [x] }) => {
      if (down) {
        const newX =
          x > 0 ? Math.min(Math.abs(limit), x) : Math.max(-Math.abs(limit), x);
        set({ xy: [newX, 0] });
        return;
      }
      set({ xy: [0, 0] });
      if (Math.abs(x) > Math.abs(limit)) {
        x <= 0 ? handleNext() : handlePrev();
      }
    },
    { axis: "lock" },
  );

  return (
    <>
      <StyledMenu $stickyOffset={stickyOffset} $noBorder={noBorder}>
        {tabs.map((tab, i) => (
          <button
            key={tab.id}
            disabled={active.id === tab.id}
            data-index={i}
            data-active={active.id === tab.id || undefined}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </StyledMenu>
      <StyledTabs>
        <StyledContent
          {...bind(50)}
          style={{
            transform:
              xy && xy.interpolate((x) => `translate3d(${x}px, 0px, 0)`),
          }}
        >
          {typeof ActiveStep === "function"
            ? ActiveStep({ active, handleNext, handlePrev })
            : ActiveStep}
        </StyledContent>
      </StyledTabs>
    </>
  );
};
Tabs.propTypes = {
  tabs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      label: PropTypes.string,
    }),
  ).isRequired,
  activeTab: PropTypes.object,
  activeIndex: PropTypes.number,
  activeTabIndex: PropTypes.number,
  onTabChange: PropTypes.func,
  onNextTab: PropTypes.func,
  onPrevTab: PropTypes.func,
  stickyOffset: PropTypes.number,
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.func]),
  noBorder: PropTypes.bool,
};
export default Tabs;
