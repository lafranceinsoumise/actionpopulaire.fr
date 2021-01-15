import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { useSpring, animated } from "react-spring";
import { useDrag } from "react-use-gesture";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const StyledMenu = styled.nav`
  position: sticky;
  z-index: 1;
  top: -1px;
  left: 0;
  right: 0;
  display: flex;
  flex-flow: row nowrap;
  padding: 0 1rem;
  background-color: white;
  border-top: 1px solid #dfdfdf;
  box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 2px 1px rgba(0, 35, 44, 0.08);
  overflow-x: auto;
  overflow-x: overlay;
  overflow-y: hidden;

  button {
    flex: 1 1 auto;
    background-color: white;
    border: none;
    height: 2.875rem;
    cursor: pointer;
    transition: all 200ms ease-in-out;
    box-shadow: none;
    color: ${style.black1000};
    white-space: nowrap;
    min-width: max-content;

    &[data-active],
    &:hover,
    &:focus {
      color: ${style.primary500};
    }

    &[data-active] {
      background-size: 100%;
      box-shadow: 0 -3px 0 ${style.primary500} inset;
    }
  }
`;
const StyledContent = styled(animated.div)``;
const StyledTabs = styled.div`
  touch-action: pan-y;
  overflow-x: hidden;
  overflow-y: auto;
`;

export const Tabs = (props) => {
  const { children, tabs } = props;

  const [activeIndex, setActiveIndex] = useState(0);
  const handleClick = useCallback((e) => {
    setActiveIndex(e.target.dataset.index);
  }, []);

  const handleNext = useCallback(() => {
    setActiveIndex((state) => Math.min(state + 1, tabs.length - 1));
  }, [tabs.length]);

  const handlePrev = useCallback(() => {
    setActiveIndex((state) => Math.max(0, state - 1));
  }, []);

  const active = useMemo(() => tabs[activeIndex] || tabs[0], [
    activeIndex,
    tabs,
  ]);

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
    { axis: "x", lockDirection: true }
  );

  return (
    <>
      <StyledMenu>
        {tabs.map((tab, i) => (
          <button
            key={tab.id}
            disabled={active.id === tab.id}
            data-index={i}
            data-active={active.id === tab.id || undefined}
            onClick={handleClick}
          >
            {tab.label}
          </button>
        ))}
      </StyledMenu>
      <StyledTabs>
        <StyledContent
          {...bind(50)}
          style={{
            transform: xy.interpolate((x) => `translate3d(${x}px, 0px, 0)`),
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
    })
  ).isRequired,
  children: PropTypes.node,
};
export default Tabs;
