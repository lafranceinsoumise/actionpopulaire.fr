import React from 'react';
import {hot} from 'react-hot-loader';
import PropTypes from 'prop-types';
import {Button, InputGroup, FormControl, Row, Col} from 'react-bootstrap';


import './style.css';


const AMOUNTS = [100, 50, 25, 15, 10];


class AmountWidget extends React.Component {
  constructor({hiddenField}) {
    super();

    this.hiddenField = hiddenField;

    this.state = {
      value: null,
      custom: false
    };
  }

  render() {
    const state = this.state;
    return <div className="amount-component" style={{display: 'flex', 'flex-wrap': 'wrap'}}>
      <input type="hidden" value={state.value ? state.value : ''} name={this.hiddenField.name}/>
      {AMOUNTS.map(value => (
        <button key={value} type="button" onClick={() => this.setState({value, custom: false})}
                className={['btn', state.custom || state.value !== value ? 'btn-default' : 'btn-primary'].join(' ')}>
          {value}&nbsp;€
        </button>))}
      <InputGroup>
        <FormControl type="number" placeholder="autre"
                     onChange={e => this.setState({value: e.target.value, custom: true})}
                     value={this.state.custom ? this.state.value : ''}/>
        <InputGroup.Addon>€</InputGroup.Addon>
      </InputGroup>
    </div>;
  }
}

AmountWidget.propTypes = {
  hiddenField: PropTypes.object
};

export default hot(module)(AmountWidget);
