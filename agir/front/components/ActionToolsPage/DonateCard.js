import PropTypes from "prop-types";
import React from "react";
import { animated, useSpring } from "@react-spring/web";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";

const StyledCard = styled.div`
  padding: 1.5rem;
  background-color: ${(props) => props.theme.redNSP};
  border-radius: ${(props) => props.theme.borderRadius};
  color: ${(props) => props.theme.white};
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;

  & > svg {
    width: 100%;
    height: 7px;
  }

  h4,
  p {
    color: inherit;
    margin: 0;
    padding: 0;
  }

  h4 {
    font-weight: 700;
    font-size: 1.5rem;
    line-height: 1.3;
  }

  p {
    font-weight: 500;
    font-size: 1rem;
    line-height: 1.5;
    font-feature-settings: "tnum";
    font-variant-numeric: tabular-nums;
  }
`;

const formatCurrency = (amount) =>
  `${Math.floor(amount / 100)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, " ")} €`;

export const DonateCard = (props) => {
  const { amount } = props;

  const target = Math.ceil(amount / 100000000) * 100000000;

  const { progress, animatedAmount } = useSpring({
    from: { progress: 0, animatedAmount: 1 },
    progress: Math.round((amount / target) * 325),
    animatedAmount: amount,
    delay: 250,
  });

  return (
    <StyledCard>
      <h4>Je fais un don pour la campagne</h4>
      <animated.p>
        <animated.span>
          {animatedAmount.to((x) => formatCurrency(x.toFixed(0)))}
        </animated.span>
        &nbsp;/&nbsp;{formatCurrency(target)}
      </animated.p>
      <svg
        width="325"
        height="7"
        viewBox={`0 0 325 7`}
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        <rect width="325" height="7" rx="0.6%" ry="3.5" fill="#B31F36" />
        <animated.rect
          width={progress}
          height="7"
          rx="0.6%"
          ry="3.5"
          fill="#FFFFFF"
        />
      </svg>
      <Button link route="donationLanding" icon="heart" color="whiteRed">
        Je fais un don
      </Button>
    </StyledCard>
  );
};
DonateCard.propTypes = {
  amount: PropTypes.number.isRequired,
};
export default DonateCard;
