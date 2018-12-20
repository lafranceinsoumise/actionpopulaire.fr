import React from "react";
import PropTypes from "prop-types";

const Question = ({ question, value, setValue, style }) => (
  <div style={style}>
    <h4>{question.question}</h4>
    <button className="btn btn-default" onClick={() => setValue(true)}>
      Oui
    </button>
    &nbsp;
    <button className="btn btn-default" onClick={() => setValue(false)}>
      Non
    </button>
  </div>
);
Question.propTypes = {
  question: PropTypes.object,
  value: PropTypes.bool,
  setValue: PropTypes.func
};

export default Question;
