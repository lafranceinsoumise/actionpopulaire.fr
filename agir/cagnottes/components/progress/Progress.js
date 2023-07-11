import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { animated, useSpring } from "@react-spring/web";
import styled from "styled-components";
import useSWR from "swr";

import { getContrastYIQ } from "@agir/lib/utils/colors";

import lfiNupesLogo from "@agir/front/genericComponents/logos/lfi-nupes.svg";

const StyledTitleLogo = styled.img``;
const StyledTitle = styled.h2`
  font-size: 50px;
  font-size: ${({ $height }) => ($height ? 0.5 * $height : "50")}px;
  line-height: 1.2;
  font-weight: 500;
  text-shadow: 0px 2px 6px #000a2c;
  color: #ffffff;
  color: ${({ $color }) => $color || "#FFFFFF"};
  margin: 0 0 8px;
  padding: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &:empty {
    display: none;
  }

  @media (max-width: 700px) {
    font-size: 24px;
    font-size: ${({ $height }) => ($height ? 0.24 * $height : "24")}px;
  }

  ${StyledTitleLogo} {
    flex: 0 0 auto;
    height: inherit;
    width: auto;
    height: 50px;
    height: ${({ $height }) => ($height ? 0.5 * $height : "50")}px;

    @media (max-width: 700px) {
      height: 24px;
      height: ${({ $height }) => ($height ? 0.24 * $height : "24")}px;
    }
  }
`;

const StyledBar = styled.div`
  width: 100%;
  height: 100px;
  height: ${({ $height }) => $height || 100}px;
  position: relative;
  overflow: hidden;

  & > * {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    margin: 0;
    width: 100%;
    height: 100%;
    min-height: 1;
  }

  &::before {
    content: "";
    display: block;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.5);
  }

  & > div {
    --point-width: 55px;
    --point-width: ${({ $height }) => ($height ? 0.55 * $height : "55")}px;

    width: 0%;
    background: #ff2e20;
    background: ${({ $color }) => $color || "#FF2E20"};
    box-sizing: content-box;
    padding-left: 55px;
    /* clip-path: polygon(
      0% 0%,
      100% 0%,
      calc(100% - var(--point-width)) 100%,
      0% 100%
    ); */
    will-change: width;
  }

  & > p {
    color: #ffffff;
    color: ${({ $color }) =>
      $color && $color[0] === "#" ? getContrastYIQ($color) : "#FFFFFF"};
    text-align: left;
    font-weight: 500;
    font-size: 80px;
    font-size: ${({ $height }) => ($height ? 0.8 * $height : "80")}px;
    line-height: 0;
    padding: 0 16px;
    padding: 0 ${({ $height }) => ($height ? 0.16 * $height : "16")}px;

    @media (max-width: 700px) {
      font-size: 48px;
      font-size: ${({ $height }) => ($height ? 0.48 * $height : "48")}px;
    }
  }
`;
const StyledPage = styled.div`
  padding: 0;
  margin: 0;
  min-width: 100vw;
  min-height: 100vh;
  font-family: Inter, Arial, Helvetica, sans-serif;
  background: transparent;
  background: ${({ $background }) => $background || "transparent"};
`;

const formatCurrency = (amount) =>
  `${Math.floor(amount / 100)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, " ")} €`;

const getTarget = (amount, goals) => {
  let target = goals.find((goal) => amount < goal);

  if (target) {
    return target;
  }

  let targetTenth = 1;
  for (let length = String(amount).length; length--; length) {
    targetTenth *= 10;
  }
  target = Math.ceil(amount / targetTenth) * targetTenth;

  return target;
};

const ProgressBar = (props) => {
  const {
    amount,
    title,
    titleColor,
    titleLogo = false,
    barColor,
    barHeight,
    goals,
  } = props;

  const steps = useMemo(
    () =>
      Array.isArray(goals)
        ? goals
            .filter((goal) => !isNaN(parseInt(goal)))
            .map((goal) => parseInt(goal))
            .sort()
        : [],
    [goals],
  );

  const target = useMemo(() => getTarget(amount, steps), [amount, steps]);
  const targetTitle = useMemo(
    () => `${formatCurrency(amount)} / ${formatCurrency(target)}`,
    [amount, target],
  );

  const { width, animatedAmount } = useSpring({
    from: { width: "0%", animatedAmount: 1 },
    width: `${Math.round((amount / target) * 100)}%`,
    animatedAmount: amount,
  });

  const height =
    barHeight && !isNaN(parseInt(barHeight)) ? parseInt(barHeight) : null;

  return (
    <>
      <StyledTitle $color={titleColor} $height={height}>
        <span>{title}</span>
        {!!titleLogo && <StyledTitleLogo src={lfiNupesLogo} />}
      </StyledTitle>
      <StyledBar $color={barColor} $height={height} title={targetTitle}>
        <animated.div style={{ width }} />
        <animated.p>{animatedAmount.to(formatCurrency)}</animated.p>
      </StyledBar>
    </>
  );
};

ProgressBar.propTypes = {
  amount: PropTypes.number,
  title: PropTypes.string,
  titleColor: PropTypes.string,
  titleLogo: PropTypes.bool,
  barColor: PropTypes.string,
  barHeight: PropTypes.number,
  goals: PropTypes.arrayOf(PropTypes.number),
};

const Progress = (props) => {
  const { amountAPI = null, background, apiRefreshInterval, ...rest } = props;
  const refreshInterval =
    apiRefreshInterval && !isNaN(parseInt(apiRefreshInterval))
      ? Math.max(Math.abs(parseInt(apiRefreshInterval)), 1000)
      : 1000;
  const { data, isLoading } = useSWR(amountAPI, { refreshInterval });

  const amount =
    data && !isNaN(parseInt(data?.totalAmount))
      ? parseInt(data.totalAmount)
      : null;

  return (
    <StyledPage $background={background}>
      {!isLoading && typeof amount === "number" && (
        <ProgressBar amount={amount} {...rest} />
      )}
    </StyledPage>
  );
};

Progress.propTypes = {
  amountAPI: PropTypes.string,
  // The interval (in milliseconds) used to refresh data from the API
  apiRefreshInterval: PropTypes.number,
  // The page background color
  background: PropTypes.string,
  // The title text
  title: PropTypes.string,
  // The title text color
  titleColor: PropTypes.string,
  // Show/hide the title logo
  titleLogo: PropTypes.bool,
  // The progress bar main color
  barColor: PropTypes.string,
  // The progress bar height (in px)
  barHeight: PropTypes.number,
  // A list of amounts (in cents) to use as 100% progress based on current amount
  goals: PropTypes.arrayOf(PropTypes.number),
};

export default Progress;
