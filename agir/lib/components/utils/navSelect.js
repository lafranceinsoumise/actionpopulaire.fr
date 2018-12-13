import React from "react";
import PropTypes from "prop-types";

class NavSelect extends React.Component {
  constructor(props) {
    super(props);
    this.state = { choices: [], error: false };
  }

  setChoice(choice) {
    return e => {
      e.preventDefault();
      let previousChoices = this.props.value;
      let newChoices;

      if (!previousChoices.includes(choice)) {
        newChoices = Array.concat(previousChoices, choice);
      } else {
        previousChoices.splice(previousChoices.indexOf(choice), 1);
        newChoices = previousChoices;
      }

      if (newChoices.length <= this.props.max) {
        this.props.onChange(newChoices);
      }
    };
  }

  render() {
    const { choices, value } = this.props;

    return (
      <div>
        <ul className="nav nav-pills">
          {choices.map(choice => (
            <li
              key={choice.value}
              className={value.includes(choice.value) ? "active" : ""}
            >
              <a href="#" onClick={this.setChoice(choice.value)}>
                <i
                  className={
                    "fa " +
                    (value.includes(choice.value)
                      ? "fa-check-circle"
                      : "fa-circle-o")
                  }
                />
                &nbsp;{choice.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  }
}
NavSelect.propTypes = {
  choices: PropTypes.array,
  value: PropTypes.array,
  onChange: PropTypes.func,
  max: PropTypes.number
};

export default NavSelect;
