import React from "react";
import PropTypes from "prop-types";
import StepZilla from "react-stepzilla";

export default function MultiStepForm({ steps, startAtStep }) {
  return (
    <div className="step-progress">
      <StepZilla
        steps={steps}
        startAtStep={startAtStep}
        stepsNavigation={true}
        showNavigation={true}
        nextButtonText="Suivant&nbsp;&rarr;"
        backButtonText="&larr;&nbsp;Précédent"
        nextButtonCls="btn btn-primary pull-right"
        backButtonCls="btn btn-default pull-left"
      />
    </div>
  );
}

MultiStepForm.propTypes = {
  steps: PropTypes.array.isRequired,
  startAtStep: PropTypes.number,
};

MultiStepForm.defaultProps = {
  startAtStep: 0,
};
