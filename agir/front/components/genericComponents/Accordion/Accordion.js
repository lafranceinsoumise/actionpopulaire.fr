import PropTypes from "prop-types";
import React, { memo, useState } from "react";
import { useSpring, a, animated } from "react-spring";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useMeasure, usePrevious } from "@agir/lib/utils/hooks";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

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
    display: grid;
    grid-template-columns: auto 1fr auto;
    grid-gap: 1rem;
    padding: 1rem 1.5rem;
    background-color: ${style.white};
    border: none;
    border-top: 1px solid ${style.black100};
    border-bottom: ${({ $open }) =>
      $open ? `1px solid ${style.black100}` : "none"};
    text-align: left;
    cursor: pointer;

    & > strong {
      font-weight: 500;
      font-size: 1rem;
      white-space: normal;
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
  const { children, icon, name, isDefaultOpen = false } = props;
  const previous = usePrevious(isOpen);
  const [bind, { height: viewHeight }] = useMeasure();

  const [isOpen, setOpen] = useState(isDefaultOpen);

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

  return (
    <Frame $open={isOpen}>
      <Title onClick={() => setOpen((state) => !state)}>
        {icon ? (
          <RawFeatherIcon width="1.5rem" height="1.5rem" name={icon} />
        ) : null}
        <strong>{name}</strong>
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
  name: PropTypes.string,
  icon: PropTypes.string,
  isDefaultOpen: PropTypes.bool,
};

export default Accordion;
