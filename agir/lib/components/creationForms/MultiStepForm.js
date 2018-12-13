import React from "react";
import PropTypes from "prop-types";
import StepZilla from "react-stepzilla";

export default function MultiStepForm({ steps }) {
  return (
    <div className="step-progress">
      <StepZilla
        steps={steps}
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
  steps: PropTypes.array
};
