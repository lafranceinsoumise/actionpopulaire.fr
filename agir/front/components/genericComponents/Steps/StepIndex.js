import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import CounterBadge from "@agir/front/app/Navigation/CounterBadge";
import {
  Hide,
  ResponsiveLayout,
  useResponsiveMemo,
} from "@agir/front/genericComponents/grid";

const StepBadge = styled(CounterBadge).attrs((props) => ({
  ...props,
  $background: props.$active ? props.theme.primary500 : props.theme.white,
  $color: props.$active ? props.theme.white : props.theme.black500,
  $border: props.$active ? "none" : props.theme.black50,
}))`
  width: 2rem;
  height: 2rem;
`;

const StyledActions = styled.div`
  display: flex;
  flex-flow: row nowrap;
  gap: 0.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-flow: column nowrap;
    align-items: stretch;
  }
`;

const StyledStep = styled.button.attrs((props) => ({
  ...props,
  type: "button",
}))`
  flex: 1 1 1rem;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  margin: 0;
  padding: 0;
  gap: 0.5rem;
  background-color: transparent;
  border: none;
  cursor: pointer;

  &[disabled] {
    cursor: default;
  }

  &:first-child {
    background: linear-gradient(
      90deg,
      white 0%,
      white 50%,
      transparent 50%,
      transparent 100%
    );
  }

  &:last-child {
    background: linear-gradient(
      -90deg,
      white 0%,
      white 50%,
      transparent 50%,
      transparent 100%
    );
  }

  &:first-child:last-child {
    background: transparent;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }

  h5 {
    margin: 0;
    color: ${(props) =>
      props.$active ? props.theme.primary500 : props.theme.black500};
    font-weight: ${(props) => (props.$active ? 600 : 400)};
    overflow-wrap: normal;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.125rem;
    }
  }
`;
const StyledSteps = styled.div`
  padding: 1rem 0;

  header {
    display: flex;
    flex-flow: row nowrap;
    align-items: start;
    gap: 6rem;

    nav {
      flex: 1 1 auto;
      display: flex;
      flex-flow: row nowrap;
      justify-content: space-between;
      align-items: stretch;
      gap: 1rem;
      padding: 0;
      background: linear-gradient(
        transparent 0%,
        transparent calc(1rem),
        ${(props) => props.theme.black100} calc(1rem),
        ${(props) => props.theme.black100} calc(1rem + 1px),
        transparent calc(1rem + 1px),
        transparent 100%
      );

      @media (max-width: ${(props) => props.theme.collapse}px) {
        background: transparent;
      }
    }
  }

  article {
    padding: 1.5rem 0;
  }
`;

const StepActions = (props) => {
  const {
    goToPrevious,
    goToNext,
    onSave,
    onSubmit,
    isLoading,
    disabled,
    ...rest
  } = props;

  const saveLabel = useResponsiveMemo(
    "Enregistrer le brouillon",
    "Enregistrer"
  );

  return (
    <StyledActions {...rest}>
      {goToPrevious && (
        <Hide
          $over
          as={Button}
          type="button"
          onClick={goToPrevious}
          disabled={isLoading}
          color="choose"
        >
          Annuler
        </Hide>
      )}
      {onSave && (
        <Button
          onClick={onSave}
          loading={isLoading}
          disabled={isLoading}
          color="default"
          icon="save"
        >
          {saveLabel}
        </Button>
      )}
      {goToNext && (
        <Button
          type="button"
          color="primary"
          onClick={goToNext}
          disabled={isLoading}
          icon="arrow-right"
        >
          Continuer
        </Button>
      )}
      {!goToNext && onSubmit ? (
        <Button
          loading={isLoading}
          disabled={disabled}
          type="submit"
          color="primary"
          icon="send"
        >
          Envoyer
        </Button>
      ) : null}
    </StyledActions>
  );
};

StepActions.propTypes = {
  as: PropTypes.string,
  goToPrevious: PropTypes.func,
  goToNext: PropTypes.func,
  onSubmit: PropTypes.func,
  onSave: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
};

const MobileLayout = (props) => {
  const {
    as = "div",
    goToPrevious,
    goToNext,
    onSubmit,
    onSave,
    isLoading,
    disabled,
    steps,
    stepNames,
    current,
  } = props;

  return (
    <StyledSteps as={as} onSubmit={onSubmit}>
      <header>
        <nav>
          <StyledStep $active>
            <StepBadge value={`${current + 1}/${steps.length}`} $active />
            <h5>{(stepNames && stepNames[current]) || null}</h5>
          </StyledStep>
        </nav>
      </header>
      <article>{steps[current]}</article>
      <StepActions
        as="footer"
        goToPrevious={
          typeof steps[current - 1] !== "undefined" ? goToPrevious : undefined
        }
        goToNext={
          typeof steps[current + 1] !== "undefined" ? goToNext : undefined
        }
        onSubmit={onSubmit}
        onSave={onSave}
        isLoading={isLoading}
        disabled={disabled}
      />
    </StyledSteps>
  );
};

MobileLayout.propTypes = {
  as: PropTypes.string,
  title: PropTypes.string,
  stepNames: PropTypes.arrayOf(PropTypes.string),
  goToPrevious: PropTypes.func,
  goToNext: PropTypes.func,
  onSubmit: PropTypes.func,
  onSave: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
  steps: PropTypes.array,
  last: PropTypes.number,
  current: PropTypes.number,
};

const DesktopLayout = (props) => {
  const {
    as = "div",
    goToPrevious,
    goToNext,
    goToStep,
    onSubmit,
    onSave,
    isLoading,
    disabled,
    steps,
    stepNames,
    current,
  } = props;

  return (
    <StyledSteps as={as} onSubmit={onSubmit}>
      <header>
        <nav>
          {steps.map((_, i) => (
            <StyledStep
              key={i}
              $active={i === current}
              onClick={() => goToStep && goToStep(i)}
              disabled={!goToStep || isLoading || i === current}
            >
              <StepBadge value={i + 1} $active={i === current} />
              <h5>{(stepNames && stepNames[i]) || null}</h5>
            </StyledStep>
          ))}
        </nav>
        <StepActions
          goToPrevious={
            typeof steps[current - 1] !== "undefined" ? goToPrevious : undefined
          }
          goToNext={
            typeof steps[current + 1] !== "undefined" ? goToNext : undefined
          }
          onSubmit={onSubmit}
          onSave={onSave}
          isLoading={isLoading}
          disabled={disabled}
        />
      </header>
      <article>{steps[current]}</article>
    </StyledSteps>
  );
};

DesktopLayout.propTypes = {
  as: PropTypes.string,
  title: PropTypes.string,
  stepNames: PropTypes.arrayOf(PropTypes.string),
  goToPrevious: PropTypes.func,
  goToNext: PropTypes.func,
  goToStep: PropTypes.func,
  onSubmit: PropTypes.func,
  onSave: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
  steps: PropTypes.array,
  last: PropTypes.number,
  current: PropTypes.number,
};

const StepIndex = (props) => {
  return (
    <ResponsiveLayout
      {...props}
      MobileLayout={MobileLayout}
      DesktopLayout={DesktopLayout}
    />
  );
};

StepIndex.propTypes = {
  as: PropTypes.string,
  title: PropTypes.string,
  stepNames: PropTypes.arrayOf(PropTypes.string),
  goToPrevious: PropTypes.func,
  goToNext: PropTypes.func,
  goToStep: PropTypes.func,
  onSubmit: PropTypes.func,
  onSave: PropTypes.func,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
  steps: PropTypes.array,
  last: PropTypes.number,
  current: PropTypes.number,
};

export default StepIndex;
