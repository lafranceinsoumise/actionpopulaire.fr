import PropTypes from "prop-types";
import React from "react";
import { animated, useSpring } from "@react-spring/web";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";

const StyledSteps = styled.div`
  padding: 1rem 0;

  header {
    text-transform: uppercase;
    color: ${(props) => props.theme.progressColor || "#0c0de8"};
    padding: 0 0 1rem;

    h5 {
      color: inherit;
      font-size: 0.875rem;
    }

    & > div {
      width: 100%;
      height: 8px;
      background-color: #f2f3fc;
      border-radius: 10px;
      overflow: hidden;

      & > div {
        background-color: currentcolor;
        height: inherit;
        border-radius: inherit;
        width: 0;
      }
    }
  }

  article {
    padding: 0.5rem 0 2rem;
  }

  footer {
    display: flex;
    flex-flow: row nowrap;
    gap: 0.5rem;
  }
`;

const StepBar = (props) => {
  const {
    as = "div",
    title,
    goToPrevious,
    goToNext,
    onSubmit,
    isLoading,
    disabled,
    steps,
    last,
    current,
  } = props;

  const { progress } = useSpring({
    initial: { progress: "0%" },
    progress: Math.round(((current + 1) / (last + 1)) * 100) + "%",
    delay: 100,
  });

  return (
    <StyledSteps as={as} onSubmit={onSubmit}>
      <header>
        <h5>{title}</h5>
        <div aria-label={`étape ${current + 1} sur ${last + 1}`}>
          <animated.div style={{ width: progress }} />
        </div>
      </header>
      <article>{steps[current]}</article>
      <footer>
        {typeof steps[current - 1] !== "undefined" && (
          <Button type="button" onClick={goToPrevious}>
            Précédent
          </Button>
        )}
        {typeof steps[current + 1] !== "undefined" && (
          <Button type="button" color="danger" onClick={goToNext}>
            Suivant
          </Button>
        )}
        {onSubmit && current === last && (
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

StepBar.propTypes = {
  as: PropTypes.string,
  title: PropTypes.string,
  goToPrevious: PropTypes.func,
  goToNext: PropTypes.func,
  onSubmit: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
  steps: PropTypes.array,
  last: PropTypes.number,
  current: PropTypes.number,
};

export default StepBar;
