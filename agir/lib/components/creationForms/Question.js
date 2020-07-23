import React from "react";
import PropTypes from "prop-types";

const Question = ({ question, setValue, style }) => (
  <div style={style}>
    <h4>{question.question}</h4>
    <p>{question.helpText}</p>
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
  setValue: PropTypes.func,
  style: PropTypes.object,
};

export default Question;
