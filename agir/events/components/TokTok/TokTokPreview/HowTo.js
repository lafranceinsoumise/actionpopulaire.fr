import PropTypes from "prop-types";
import React, { useState } from "react";
import { animated, useSpring } from "@react-spring/web";
import { usePrevious } from "react-use";
import styled from "styled-components";

import { useLocalStorage, useMeasure } from "@agir/lib/utils/hooks";

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
  padding: 0 0 1rem;
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
            <RawFeatherIcon strokeWidth={2} name="edit-2" />
            <span>
              <strong>Notez les adresses</strong> que vous avez couvertes pour
              mieux partager le travail avec les autres groupes
            </span>
          </li>
          <li>
            <RawFeatherIcon strokeWidth={2} name="map-pin" />
            <span>
              <strong>Ciblez les quartiers</strong> lorsque vous préparez vos
              actions grâce aux indications sur la carte
            </span>
          </li>
          <li>
            <RawFeatherIcon strokeWidth={2} name="bar-chart-2" />
            <span>
              <strong>
                Affichez les intentions de vote et taux d'absention
              </strong>{" "}
              par secteur en cliquant sur le menu en haut à droite
            </span>
          </li>
          <li>
            <RawFeatherIcon strokeWidth={2} name="search" />
            <span>
              <strong>Zoomez au niveau de votre ville et votre rue</strong> pour
              voir les quartiers prioritaires où nos actions sont
              attendues&nbsp;!
            </span>
          </li>
        </StyledBody>
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
    "AP__toktokhowto",
    false
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
