import PropTypes from "prop-types";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import StepBar from "./StepBar";
import StepIndex from "./StepIndex";
import { scrollToElement } from "@agir/front/app/utils";

export const STEPPER = {
  bar: StepBar,
  index: StepIndex,
  default: StepBar,
};

export const useSteps = (initialStep = 0) => {
  const [step, setStep] = useState(initialStep);
  const goToPrevious = useCallback(() => setStep((step) => step - 1), []);
  const goToNext = useCallback(() => setStep((step) => step + 1), []);
  const goToStep = useCallback((step) => {
    setStep(step);
  }, []);

  return [step, goToPrevious, goToNext, goToStep];
};

const ControlledSteps = (props) => {
  const { type, step, children, ...rest } = props;
  const topRef = useRef();
  const shouldScrollToTop = useRef(false);
  const steps = children.filter(Boolean);
  const stepsArray = React.Children.toArray(steps);
  const lastStep = React.Children.count(steps) - 1;
  const currentStep = Math.min(Math.max(step, 0), lastStep);

  useEffect(() => {
    if (shouldScrollToTop.current) {
      topRef.current &&
        scrollToElement(topRef.current.parentElement, window, 150);
    } else {
      shouldScrollToTop.current = true;
    }
  }, [currentStep]);

  const Stepper = useMemo(
    () => (type && STEPPER[type] ? STEPPER[type] : STEPPER.default),
    [type]
  );

  return (
    <>
      <div ref={topRef} aria-hidden />
      <Stepper
        {...rest}
        topRef={topRef}
        steps={stepsArray}
        last={lastStep}
        current={currentStep}
      />
    </>
  );
};

ControlledSteps.propTypes = {
  type: PropTypes.oneOf(Object.keys(STEPPER)),
  step: PropTypes.number.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]),
};

const UncontrolledSteps = (props) => {
  const [step, goToPrevious, goToNext, goToStep] = useSteps();

  return (
    <ControlledSteps
      {...props}
      step={step}
      goToPrevious={goToPrevious}
      goToNext={goToNext}
      goToStep={goToStep}
    />
  );
};

const Steps = (props) =>
  typeof props.step === "number" && props.goToPrevious && props.goToNext ? (
    <ControlledSteps {...props} />
  ) : (
    <UncontrolledSteps {...props} />
  );

Steps.propTypes = {
  type: PropTypes.oneOf(Object.keys(STEPPER)),
  step: PropTypes.number,
  goToPrevious: PropTypes.func,
  goToNext: PropTypes.func,
  goToStep: PropTypes.func,
};

export default Steps;
