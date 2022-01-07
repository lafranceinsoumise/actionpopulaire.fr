import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { animated, useSpring } from "@react-spring/web";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";

const StyledSteps = styled.div`
  padding: 1rem 0;

  header {
    text-transform: uppercase;
    color: #0c0de8;
    padding: 0 0 1rem;

    h5 {
      color: inherit;
      font-size: 0.875rem;
    }

    & > svg {
      width: 100%;
      height: 20px;
      fill: #f2f3fc;
    }

    & > div {
      width: 100%;
      height: 20px;
      background-color: #f2f3fc;
      border-radius: 10px;
      overflow: hidden;

      & > div {
        background-color: #0c0de8;
        height: inherit;
        width: 0;
      }
    }
  }

  article {
    padding: 1rem 0 2rem;
  }

  footer {
    display: flex;
    flex-flow: row nowrap;
    gap: 0.5rem;
  }
`;

export const useSteps = (initialStep = 0) => {
  const [step, setStep] = useState(initialStep);
  const goToPrevious = useCallback(() => setStep((step) => step - 1), []);
  const goToNext = useCallback(() => setStep((step) => step + 1), []);

  return [step, goToPrevious, goToNext, setStep];
};

const ControlledSteps = (props) => {
  const {
    as = "div",
    title,
    step,
    goToPrevious,
    goToNext,
    onSubmit,
    isLoading,
    disabled,
    children,
  } = props;

  const topRef = useRef();
  const lastStep = React.Children.count(children) - 1;
  const currentStep = Math.min(Math.max(step, 0), lastStep);

  const { progress, animatedAmount } = useSpring({
    initial: { progress: "0%" },
    progress: Math.round(((currentStep + 1) / (lastStep + 1)) * 100) + "%",
    delay: 100,
  });

  const childrenArray = React.Children.toArray(children);

  useEffect(() => {
    topRef.current && topRef.current.scrollIntoView(true);
  }, [currentStep]);

  return (
    <StyledSteps as={as} onSubmit={onSubmit} ref={topRef}>
      <header>
        <h5>{title}</h5>
        <div aria-label={`étape ${currentStep + 1} sur ${lastStep + 1}`}>
          <animated.div style={{ width: progress }} />
        </div>
      </header>
      <article>{childrenArray[currentStep]}</article>
      <footer>
        {typeof childrenArray[currentStep - 1] !== "undefined" && (
          <Button type="button" onClick={goToPrevious}>
            Précédent
          </Button>
        )}
        {typeof childrenArray[currentStep + 1] !== "undefined" && (
          <Button type="button" color="danger" onClick={goToNext}>
            Suivant
          </Button>
        )}
        {onSubmit && step === lastStep && (
          <Button
            loading={isLoading}
            disabled={disabled}
            type="submit"
            color="danger"
          >
            Envoyer
          </Button>
        )}
      </footer>
    </StyledSteps>
  );
};

ControlledSteps.propTypes = {
  as: PropTypes.string,
  title: PropTypes.string,
  step: PropTypes.number.isRequired,
  goToPrevious: PropTypes.func.isRequired,
  goToNext: PropTypes.func.isRequired,
  onSubmit: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
};

const UncontrolledSteps = (props) => {
  const [step, goToPrevious, goToNext] = useSteps();

  return (
    <ControlledSteps
      {...props}
      step={step}
      goToPrevious={goToPrevious}
      goToNext={goToNext}
    />
  );
};

UncontrolledSteps.propTypes = {
  as: PropTypes.string,
  title: PropTypes.string,
  onSubmit: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
};

const Steps = (props) =>
  props.step && props.goToPrevious && props.goToNext ? (
    <ControlledSteps {...props} />
  ) : (
    <UncontrolledSteps {...props} />
  );

Steps.propTypes = {
  as: PropTypes.string,
  title: PropTypes.string,
  step: PropTypes.number,
  goToPrevious: PropTypes.func,
  goToNext: PropTypes.func,
  onSubmit: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
};

export default Steps;
