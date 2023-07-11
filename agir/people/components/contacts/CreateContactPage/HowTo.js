import PropTypes from "prop-types";
import React, { useState } from "react";
import { animated, useSpring } from "@react-spring/web";
import { usePrevious } from "react-use";
import styled from "styled-components";

import { useLocalStorage, useMeasure } from "@agir/lib/utils/hooks";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledHeader = styled.button`
  background-color: transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: none;
  outline: none;
  cursor: pointer;
  width: 100%;
  height: 3.5rem;
  padding: 0;
  margin: 0;

  span {
    transform-origin: "center center";
    line-height: 0;
  }
`;

const StyledBody = styled(animated.ul)`
  list-style: none;
  padding: 0;
  margin: 0;

  & > li {
    display: flex;
    align-items: flex-start;
    padding-bottom: 0.5rem;

    strong {
      font-weight: 600;
    }

    & > * {
      flex: 1 1 auto;
      font-size: 0.875rem;
      line-height: 1.5;

      &:first-child {
        flex: 0 0 auto;
        margin-right: 1rem;
        color: ${(props) => props.theme.primary500};
      }
    }
  }
`;
const StyledFooter = styled(animated.footer)`
  padding: 0.5rem 0 1rem;

  ${Button} {
    margin-left: 2.5rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      width: 100%;
      margin-left: 0;
    }
  }
`;
const StyledCard = styled(animated.div)`
  padding: 0 1rem;
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  overflow: hidden;
`;

export const HowTo = (props) => {
  const { isInitiallyCollapsed, onClose } = props;
  const [isCollapsed, setIsCollapsed] = useState(isInitiallyCollapsed);
  const wasCollapsed = usePrevious(isCollapsed);

  const open = () => setIsCollapsed(false);
  const close = () => {
    onClose();
    setIsCollapsed(true);
  };

  const [bind, { height: viewHeight }] = useMeasure();

  const { height, opacity, transform } = useSpring({
    height: isCollapsed ? 56 : viewHeight,
    opacity: isCollapsed ? 0.33 : 1,
    transform: isCollapsed ? "rotate(0deg)" : "rotate(180deg)",
    config: {
      mass: 1,
      tension: 270,
      friction: !isCollapsed ? 26 : 36,
      clamp: true,
    },
  });

  return (
    <StyledCard
      style={{
        // Prevent animation if initially opened
        height: !isCollapsed && wasCollapsed === isCollapsed ? "auto" : height,
      }}
    >
      <div {...bind}>
        <StyledHeader type="button" onClick={isCollapsed ? open : close}>
          <strong>Comment ça marche</strong>
          <animated.span style={{ transform }}>
            <RawFeatherIcon name="chevron-down" />
          </animated.span>
        </StyledHeader>
        <StyledBody style={{ opacity }}>
          <li>
            <RawFeatherIcon strokeWidth={2} name="check-square" />
            <span>
              <strong>Faites rejoindre Action populaire</strong> à de nouvelles
              personnes&nbsp;!
            </span>
          </li>
          <li>
            <RawFeatherIcon strokeWidth={2} name="rss" />
            <span>
              <strong>Obtenez des contacts pour votre groupe d’action</strong>
              <br />
              Les contacts sont enregistrés et visibles dans la partie gestion
              du groupe pour les gestionnaires et animateur·ices
            </span>
          </li>
          <li>
            <RawFeatherIcon strokeWidth={2} name="map-pin" />
            <span>
              <strong>
                Essayez de recruter des correspondant·es d’immeuble ou de
                village,
              </strong>{" "}
              qui pourront diffuser nos propositions et inciter leurs voisins à
              aller voter
            </span>
          </li>
        </StyledBody>
        <StyledFooter style={{ opacity }}>
          <Button
            tabIndex={isCollapsed ? "-1" : undefined}
            type="button"
            onClick={close}
          >
            Compris
          </Button>
        </StyledFooter>
      </div>
    </StyledCard>
  );
};
HowTo.propTypes = {
  isInitiallyCollapsed: PropTypes.bool,
  onClose: PropTypes.func,
};

const ConnectedHowTo = (props) => {
  const [isInitiallyCollapsed, setIsInitiallyCollapsed] = useLocalStorage(
    "AP__contacthowto",
    false,
  );

  return (
    <HowTo
      {...props}
      isInitiallyCollapsed={isInitiallyCollapsed}
      onClose={() => setIsInitiallyCollapsed(true)}
    />
  );
};

export default ConnectedHowTo;
