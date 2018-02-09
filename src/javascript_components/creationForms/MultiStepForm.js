import React from 'react';
import PropTypes from 'prop-types';
import StepZilla from 'react-stepzilla';


export default function MultiStepForm({steps}) {
  return (
    <div className="step-progress">
      <StepZilla steps={steps} stepsNavigation={false} showNavigation={false} preventEnterSubmission={true}/>
    </div>
  );
}

MultiStepForm.propTypes = {
  steps: PropTypes.array
};
