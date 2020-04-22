import ReactDOM from "@hot-loader/react-dom";
import React, { useState } from "react";
import PropTypes from "prop-types";

const defaultGetInitial = field => field.value || null;
const defaultGetProps = () => ({});
const defaultGetValue = value =>
  value ? (typeof value === "string" ? value : value.value) : "";

export function getStatefulRenderer(
  Field,
  selector,
  {
    getInitial = defaultGetInitial,
    getProps = defaultGetProps,
    getValue = defaultGetValue
  }
) {
  return () => {
    const fieldsToReplace = document.querySelectorAll(selector);

    for (let field of fieldsToReplace) {
      const insertingNode = field.parentNode;
      const props = {
        initial: getInitial(field),
        name: field.name,
        fieldProps: getProps(field)
      };
      insertingNode.removeChild(field);
      ReactDOM.render(
        <RootComponent Field={Field} getValue={getValue} {...props} />,
        insertingNode
      );
    }
  };
}

export const RootComponent = ({
  name,
  initial,
  Field,
  getValue,
  fieldProps
}) => {
  const [value, setValue] = useState(initial);

  return (
    <>
      <input type="hidden" name={name} value={getValue(value)} />
      <Field value={value} onChange={setValue} {...fieldProps} />
    </>
  );
};
RootComponent.propTypes = {
  name: PropTypes.string,
  initial: PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.string
  }),
  Field: PropTypes.elementType,
  getValue: PropTypes.func,
  fieldProps: PropTypes.object
};
