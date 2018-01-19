import React from 'react';
import ReactDOM from 'react-dom';

class NavSelect extends React.Component {
  constructor(props) {
    super(props);
    this.max = props.max;
    this.choices = props.choices;
    this.onChange = props.onChange;
    this.state = {choices: [], error: false};
    this.setChoice = this.setChoice.bind(this);
  }

  setChoice(choice) {
    let previousChoices = this.state.choices;
    let newChoices;

    if (!previousChoices.includes(choice)) {
      newChoices = Array.concat(previousChoices, choice);
    } else {
      previousChoices.splice(previousChoices.indexOf(choice), 1);
      newChoices = previousChoices;
    }

    if (newChoices.length > this.max) {
      return this.setState({error: `Vous devez faire maximum ${this.max} choix.`});
    }

    this.setState({error: false, choices: newChoices});

    if (typeof this.onChange === 'function') {
      this.onChange(newChoices);
    }
  }

  render () {
    return (
      <div>
        {this.state.error &&
          <div className="alert alert-warning">
            <p>{this.state.error}</p>
          </div>
        }
        <ul className="nav nav-pills">
          {this.choices.map(choice => (
            <li key={choice.value} className={this.state.choices.includes(choice.value) ? 'active': ''}>
              <a href="#" onClick={(e) => (this.setChoice(choice.value))}>
                <i className={'fa ' + (this.state.choices.includes(choice.value) ? 'fa-check-circle': 'fa-circle-o')} />&nbsp;{ choice.label }
                </a>
            </li>
          ))}
        </ul>
      </div>
    )
  }


}

export default NavSelect;