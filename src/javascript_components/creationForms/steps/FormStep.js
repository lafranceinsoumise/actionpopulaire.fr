import React from 'react';
import PropTypes from 'prop-types';

export default class FormStep extends React.Component {
  constructor(props) {
    super(props);
    this.state = {errors: {}};
    this.errorCache = {};
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;
    this.props.setFields({[name]: value});
  }

  resetErrors() {
    this.setState({errors: {}});
    this.errorCache = {};
  }

  setError(field, message) {
    this.setState(state => ({errors: Object.assign({}, state.errors, {[field]: message})}));
    this.errorCache[field] = true;
  }

  clearError(field) {
    this.setState(state => ({errors: Object.assign({}, state.errors, {[field]: null})}));
    this.errorCache[field] = false;
  }

  hasError(field) {
    return this.errorCache[field];
  }

  hasErrors() {
    return Object.keys(this.errorCache).some((field) => this.errorCache[field]);
  }

  showError(field) {
    return this.state.errors[field] ? <span className="help-block">{this.state.errors[field]}</span> : null;
  }

  setField(field) {
    return (value) => this.props.setFields({[field]: value});
  }
}

FormStep.propTypes = {
  setFields: PropTypes.func,
  jumpToStep: PropTypes.func,
  fields: PropTypes.object,
};
