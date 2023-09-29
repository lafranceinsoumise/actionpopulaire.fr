import { animated, useSpring } from "@react-spring/web";
import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import { usePrevious } from "react-use";
import styled, { useTheme } from "styled-components";

import FaIcon from "@agir/front/genericComponents/FaIcon";
import ParsedString from "@agir/front/genericComponents/ParsedString";

export const STATUS_CONFIG = {
  // DRAFT
  D: {
    id: "D",
    icon: "file-pen",
    label: "Brouillon à compléter",
    color: "black500",
  },
  // AWAITING_PEER_REVIEW
  G: {
    id: "G",
    icon: "user-clock",
    label: "En attente de vérification par une autre personne",
    color: "vermillon",
  },
  // AWAITING_ADMIN_REVIEW
  R: {
    id: "R",
    icon: "user-unlock",
    label:
      "En attente de vérification par l'équipe de suivi des questions financières",
    shortLabel: "En attente de vérification par l'équipe de suivi",
    color: "black500",
  },
  // AWAITING_SUPPLEMENTARY_INFORMATION
  I: {
    id: "I",
    icon: "message-question",
    label: "Informations supplémentaires requises",
    color: "vermillon",
  },
  // VALIDATED
  V: {
    id: "V",
    icon: "check-double",
    label:
      "Validée par l'équipe de suivi des questions financières, en attente des fonds",
    shortLabel: "Validée, en attente des fonds",
    color: "green500",
  },
  // TO_PAY
  T: {
    id: "T",
    icon: "euro-sign",
    label: "Décomptée de l'allocation du groupe, à payer",
    shortLabel: "Validée, en attente de paiement",
    color: "redNSP",
  },
  // PAID
  P: {
    id: "P",
    icon: "check",
    label: "Payée",
    color: "green500",
  },
  // REFUSED
  B: {
    id: "B",
    icon: "xmark",
    label: "Cette demande a été refusée",
    shortLabel: "Refusée",
    color: "redNSP",
  },
};

const StyledStatus = styled.div`
  display: inline-flex;
  flex-flow: row nowrap;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0.5rem;
  font-size: 1rem;
  font-weight: 400;
  background-color: transparent;
  min-height: 1px;
  max-width: 100%;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 0.875rem;
    padding: 0.5rem 2rem;
    margin: 0 -1.5rem;
    max-width: 100vw;
  }

  & > i {
    width: 2rem;
    flex: 0 0 auto;
  }

  & > span {
    flex: 1 1 auto;
  }
`;

const StyledExplanation = styled(ParsedString)`
  padding: 0 0 0 3.5rem;
  font-size: 0.875rem;
  margin: 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 0;
    font-size: 0.75rem;
  }
`;

const StyledWrapper = styled.div`
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  width: 100%;
`;

const SpendingRequestStatus = (props) => {
  const { code, explanation } = props;

  const theme = useTheme();
  const [isHighlighted, setIsHighlighted] = useState();

  const config = STATUS_CONFIG[code];
  const label = props.label || config.label;
  const color = theme[config.color] || config.color;

  const previousLabel = usePrevious(label);

  const handleDoubleClick = useCallback(
    () => !isHighlighted && setIsHighlighted(true),
    [isHighlighted],
  );

  const [style] = useSpring(() => {
    const from = {
      color,
      backgroundColor: theme.white,
    };

    return {
      from,
      to: [
        {
          color: theme.primary500,
          backgroundColor: theme.primary50,
        },
        from,
      ],
      immediate: !isHighlighted,
      pause: !isHighlighted,
      onRest: ({ finished }) => finished && setIsHighlighted(false),
    };
  }, [color, theme, isHighlighted]);

  useEffect(() => {
    if (previousLabel !== label && !!previousLabel && !!label) {
      setIsHighlighted(true);
    }
  }, [previousLabel, label]);

  return (
    <StyledWrapper>
      <StyledStatus
        style={{ backgroundColor: style.backgroundColor }}
        as={animated.div}
        title={label}
        onDoubleClick={handleDoubleClick}
      >
        <FaIcon
          as={animated.i}
          style={{ color: style.color }}
          icon={config.icon + ":light"}
          size="1.5rem"
        />
        <span>{label}</span>
      </StyledStatus>
      <StyledExplanation>{explanation}</StyledExplanation>
    </StyledWrapper>
  );
};
SpendingRequestStatus.propTypes = {
  label: PropTypes.string,
  code: PropTypes.oneOf(["D", "G", "R", "I", "V", "T", "P", "B"]),
  explanation: PropTypes.string,
};

export default SpendingRequestStatus;
