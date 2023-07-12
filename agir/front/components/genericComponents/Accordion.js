/* eslint-disable react/display-name */
import { a, animated, useSpring } from "@react-spring/web";
import PropTypes from "prop-types";
import React, { memo, useEffect, useRef, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useMeasure, usePrevious } from "@agir/lib/utils/hooks";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import CounterBadge from "../app/Navigation/CounterBadge";

const Title = styled.button``;
const Content = styled(animated.div)``;
const Frame = styled.div`
  position: relative;
  padding: 0;
  margin: 0;
  width: 100%;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow-x: hidden;

  ${Title} {
    width: 100%;
    display: flex;
    gap: 1.5rem;
    padding: ${(props) => (props.$small ? "0.5rem" : "1rem 1.5rem")};
    background-color: ${style.white};
    border: none;
    border-top: ${(props) =>
      props.$small ? "none" : `1px solid ${style.black100}`};
    border-bottom: ${({ $open }) =>
      $open ? `1px solid ${style.black100}` : "none"};
    text-align: left;
    cursor: pointer;

    &:focus {
      background-color: ${style.black50};
    }

    ${RawFeatherIcon} {
      width: ${(props) => (props.$small ? 1 : 1.5)}rem;
      height: ${(props) => (props.$small ? 1 : 1.5)}rem;
    }

    & > strong {
      font-weight: ${(props) => (props.$small ? 600 : 500)};
      font-size: ${(props) => (props.$small ? 0.875 : 1)}rem;
      white-space: normal;
      flex-grow: 1;
      vertical-align: middle;
      display: flex;
      align-items: center;

      ${CounterBadge} {
        width: 1.25rem;
        height: 1.25rem;
        margin-left: 0.4rem;
        fill: ${style.primary100};

        text {
          fill: ${style.primary500};
        }
      }
    }
  }

  ${Content} {
    will-change: opacity, height;
    padding: 0;
    overflow: hidden;
    background-color: white;

    & > * {
      overflow: auto;
      white-space: normal;
    }
  }
`;

const Accordion = memo((props) => {
  const {
    children,
    icon,
    name,
    counter,
    isDefaultOpen = false,
    small = false,
  } = props;
  const [bind, { height: viewHeight }] = useMeasure();

  const [isOpen, setOpen] = useState(isDefaultOpen);
  const previous = usePrevious(isOpen);

  const { height, opacity } = useSpring({
    from: { height: 0, opacity: 0 },
    to: {
      height: isOpen ? viewHeight : 0,
      opacity: isOpen ? 1 : 0.5,
    },
    config: {
      mass: 1,
      tension: 270,
      friction: isOpen ? 26 : 36,
    },
  });

  const contentRef = useRef();
  useEffect(() => {
    const controls = contentRef.current.querySelectorAll(
      "a, input, select, textarea, button",
    );
    controls.forEach((control) => {
      control.tabIndex = isOpen ? "0" : "-1";
    });
  }, [isOpen]);

  return (
    <Frame $open={isOpen} $small={small}>
      <Title type="button" onClick={() => setOpen((state) => !state)}>
        {icon ? (
          <RawFeatherIcon
            width={small ? "1rem" : "1.5rem"}
            height={small ? "1rem" : "1.5rem"}
            name={icon}
          />
        ) : null}
        <strong>
          {name}
          {typeof counter === "number" && <CounterBadge value={counter} />}
        </strong>
        <RawFeatherIcon
          width="1.5rem"
          height="1.5rem"
          name={isOpen ? "chevron-up" : "chevron-down"}
        />
      </Title>
      <Content
        style={{
          height: isOpen && previous === isOpen ? "auto" : height,
        }}
        aria-hidden={isOpen ? "false" : "true"}
        tabIndex={isOpen ? "1" : "-1"}
        ref={contentRef}
      >
        <a.div style={{ opacity }} {...bind}>
          {children}
        </a.div>
      </Content>
    </Frame>
  );
});

Accordion.propTypes = {
  children: PropTypes.node,
  icon: PropTypes.string,
  name: PropTypes.string,
  counter: PropTypes.number,
  isDefaultOpen: PropTypes.bool,
  small: PropTypes.bool,
};

export default Accordion;
