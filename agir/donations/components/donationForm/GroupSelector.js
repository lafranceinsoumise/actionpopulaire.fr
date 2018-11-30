import React from 'react';
import PropTypes from 'prop-types';


const GroupSelector = ({choices, value, onGroupChange}) => (
  <div className="form-group">
    <label htmlFor="group-selector">Souhaitez-vous affecter votre don à un groupe d'action spécifique ?</label>
    <select className="form-control" id="group-selector" name="group" value={value} onChange={(e) => onGroupChange(e.target.value)}>
      {
        choices.map(({value, label}) => <option key={value} value={value}>{label}</option>)
      }
    </select>
  </div>
);
GroupSelector.propTypes = {
  choices: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.string,
    label: PropTypes.string
  })),
  value: PropTypes.string,
  onGroupChange: PropTypes.func
};

export default GroupSelector;