import React from "react";
import PropTypes from 'prop-types';

export default class FormStep extends React.Component {
  constructor(props) {
    super(props);
    this.setFields = props.setFields;
    this.jumpToStep = props.jumpToStep;
    this.state = {errors: {}};
  }
}

FormStep.propTypes = {
  setFields: PropTypes.func,
  jumpToStep: PropTypes.func
};
