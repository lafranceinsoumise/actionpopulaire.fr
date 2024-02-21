import { animated, useSpring } from "@react-spring/web";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { usePrevious } from "react-use";
import styled from "styled-components";

import { useMeasure } from "@agir/lib/utils/hooks";

import Link from "@agir/front/app/Link";
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

const StyledBody = styled(animated.div)`
  font-size: 0.875rem;
  line-height: 1.5;
  padding-bottom: 0.5rem;

  ul {
    list-style: none;
    padding: 0;
    margin: 0;

    & > li {
      display: flex;
      align-items: flex-start;
      padding-bottom: 0.5rem;
      gap: 1rem;

      strong {
        font-weight: 600;
      }

      & > * {
        flex: 1 1 auto;

        &:first-child {
          flex: 0 0 auto;
          color: ${(props) => props.theme.primary500};
        }
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

export const ReferentReplacementWarning = (props) => {
  const { group } = props;
  const [isCollapsed, setIsCollapsed] = useState(false);
  const wasCollapsed = usePrevious(isCollapsed);

  const open = () => setIsCollapsed(false);
  const close = () => {
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
          <strong>Détails</strong>
          <animated.span style={{ transform }}>
            <RawFeatherIcon name="chevron-down" />
          </animated.span>
        </StyledHeader>
        <StyledBody style={{ opacity }}>
          <ul>
            <li>
              <RawFeatherIcon strokeWidth={2} name="arrow-right" />
              <span>
                Par cette demande, vous vous engagez à ce que cette décision
                soit concertée avec les autres membres de votre groupe, à
                commencer par votre co-animateur·rice de groupe.
              </span>
            </li>
            <li>
              <RawFeatherIcon strokeWidth={2} name="arrow-right" />
              <span>
                Conformément à la{" "}
                <Link route="charteEquipes" target="_blank">
                  Charte des groupes d'action
                </Link>
                , l'animation du groupe doit être paritaire.
              </span>
            </li>
            <li>
              <RawFeatherIcon strokeWidth={2} name="arrow-right" />
              <span>
                La personne que vous nous indiquez doit être inscrite sur le
                site de la France insoumise et être membre de votre groupe
                d'action. Elle doit par ailleurs avoir consenti à faire partie
                de l'animation.
              </span>
            </li>
            <li>
              <RawFeatherIcon strokeWidth={2} name="arrow-right" />
              <span>
                Si vous souhaitez supprimer votre groupe d'action, merci de
                remplir{" "}
                <Link
                  href={group?.routes?.animationChangeRequest}
                  target="_blank"
                >
                  cet autre formulaire
                </Link>
                .
              </span>
            </li>
          </ul>
        </StyledBody>
      </div>
    </StyledCard>
  );
};
ReferentReplacementWarning.propTypes = {
  group: PropTypes.shape({
    routes: PropTypes.object,
  }),
};

export default ReferentReplacementWarning;
