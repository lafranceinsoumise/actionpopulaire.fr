import React from 'react';
import PropTypes from 'prop-types';

export default class FormStep extends React.Component {
  constructor(props) {
    super(props);
    this.setFields = props.setFields;
    this.jumpToStep = props.jumpToStep;
    this.state = {errors: {}, fields: {}};
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;
    this.setState({
      fields: Object.assign(this.state.fields, {[name]: value}),
    });
  }
}

FormStep.propTypes = {
  setFields: PropTypes.func,
  jumpToStep: PropTypes.func,
  fields: PropTypes.object,
};
