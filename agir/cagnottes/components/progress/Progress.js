import PropTypes from "prop-types";
import React from "react";
import { animated, useSpring } from "@react-spring/web";
import styled from "styled-components";
import useSWR from "swr";

const getContrastYIQ = (hexcolor) => {
  var r = parseInt(hexcolor.substring(1, 3), 16);
  var g = parseInt(hexcolor.substring(3, 5), 16);
  var b = parseInt(hexcolor.substring(5, 7), 16);
  var yiq = (r * 299 + g * 587 + b * 114) / 1000;
  return yiq >= 128 ? "#000000" : "#FFFFFF";
};

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
    background-color: #ff2e20;
    background-color: ${({ $color }) => $color || "#FF2E20"};
    box-sizing: content-box;
    padding-left: 55px;
    clip-path: polygon(
      0% 0%,
      100% 0%,
      calc(100% - var(--point-width)) 100%,
      0% 100%
    );
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
  }
`;
const StyledPage = styled.div`
  padding: 0;
  margin: 0;
  min-width: 100vw;
  min-height: 100vh;
  font-family: mostra-nuova, Arial, Helvetica, sans-serif;
  background-color: transparent;
  background-color: ${({ $background }) => $background || "transparent"};
`;

const formatCurrency = (amount) =>
  `${Math.floor(amount / 100)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, " ")} €`;

const getTarget = (amount) => {
  let targetTenth = 1;
  for (let length = String(amount).length; length--; length) {
    targetTenth *= 10;
  }
  return Math.ceil(amount / targetTenth) * targetTenth;
};

const ProgressBar = (props) => {
  const { amount, barColor, titleColor, barHeight } = props;
  const target = getTarget(amount);

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
        Merci pour les caisses de grève&nbsp;!
      </StyledTitle>
      <StyledBar $color={barColor} $height={height}>
        <animated.div style={{ width }} />
        <animated.p>{animatedAmount.to(formatCurrency)}</animated.p>
      </StyledBar>
    </>
  );
};

ProgressBar.propTypes = {
  amount: PropTypes.number,
  barColor: PropTypes.string,
  titleColor: PropTypes.string,
  barHeight: PropTypes.string,
};

const Progress = (props) => {
  const { amountAPI = null, background, ...rest } = props;
  const { data, isLoading } = useSWR(amountAPI, { refreshInterval: 1000 });

  const amount =
    data?.totalAmount && !isNaN(parseInt(data.totalAmount))
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
  background: PropTypes.string,
  barColor: PropTypes.string,
  titleColor: PropTypes.string,
};

export default Progress;
