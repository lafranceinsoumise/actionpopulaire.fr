import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { animated, useSpring } from "@react-spring/web";
import useSWR from "swr";


import lfiNupesLogo from "@agir/front/genericComponents/logos/lfi-nupes.svg";

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
    titleLogo = false,
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

  return (
    <>{title &&
      <h2>
        <span>{title}</span>
        {!!titleLogo && <img src={lfiNupesLogo} alt={"Logo LFI/NUPES"} />}
      </h2>}
      <div title={targetTitle} className="bar">
        <animated.div className="fill" style={{ width }} />
        <animated.p className="text">{animatedAmount.to(formatCurrency)}</animated.p>
      </div>
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
  const { amountAPI = null, apiRefreshInterval, className = '',...rest } = props;
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
    <div className={`progress ${className}`}>
      {!isLoading && typeof amount === "number" && (
        <ProgressBar amount={amount} {...rest} />
      )}
    </div>
  );
};

Progress.propTypes = {
  amountAPI: PropTypes.string,
  // The interval (in milliseconds) used to refresh data from the API
  apiRefreshInterval: PropTypes.number,
  // The page background color
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
  // a class name to add
  className: PropTypes.string,
};

export default Progress;
