import isPropValid from "@emotion/is-prop-valid";
import { createRoot } from "react-dom/client";
import React, { useState } from "react";
import PropTypes from "prop-types";

const defaultGetInitial = (field) => field.value || null;
const defaultGetProps = () => ({});
const defaultGetValue = (value) =>
  value ? (typeof value === "string" ? value : value.value) : "";

// Permet d'afficher un champ controlé Field à l'emplacement défini par selector
// avec gestion automatique de l'état. Une valeur initiale peut etre défini en
// passant une fonction `getInitial'. D'autres propriétés peuvent etre ajoutées
// avec une fonction`getProps'.
export function getStatefulRenderer(
  Field,
  selector,
  {
    getInitial = defaultGetInitial,
    getProps = defaultGetProps,
    valueToString = defaultGetValue,
  },
) {
  return () => {
    const fieldsToReplace = document.querySelectorAll(selector);

    for (let field of fieldsToReplace) {
      const insertingNode = field.parentNode;
      const props = {
        initial: getInitial(field),
        name: field.name,
        fieldProps: getProps(field),
      };
      insertingNode.removeChild(field);
      renderReactComponent(
        <RootComponent
          Field={Field}
          valueToString={valueToString}
          {...props}
        />,
        insertingNode,
      );
    }
  };
}

// Transforme n'importe quel champ controlé en un composant
// qui gère son état lui-meme
export const RootComponent = ({
  name,
  initial,
  Field,
  valueToString,
  fieldProps,
}) => {
  const [value, setValue] = useState(initial);

  return (
    <>
      <input type="hidden" name={name} value={valueToString(value)} />
      <Field value={value} onChange={setValue} {...fieldProps} />
    </>
  );
};
RootComponent.propTypes = {
  name: PropTypes.string,
  initial: PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.string,
  }),
  Field: PropTypes.elementType,
  valueToString: PropTypes.func,
  fieldProps: PropTypes.object,
};

export const renderReactComponent = (
  (roots = []) =>
  (component, node) => {
    if (!node) {
      return;
    }
    let root = roots.find((r) => r.node === node)?.root;
    if (!root) {
      root = createRoot(node);
      roots.push({ root, node });
    }

    root.render(<React.StrictMode>{component}</React.StrictMode>);
  }
)();

export const mergeRefs = (...refs) => {
  const filteredRefs = refs.filter(Boolean);
  if (!filteredRefs.length) return null;
  if (filteredRefs.length === 0) return filteredRefs[0];
  return (inst) => {
    for (const ref of filteredRefs) {
      if (typeof ref === "function") {
        ref(inst);
      } else if (ref) {
        ref.current = inst;
      }
    }
  };
};

export const validProps = (props) =>
  Object.entries(props)
    .filter(([k]) => isPropValid(k))
    .reduce((o, [_k, v]) => ({ ...o, k: v }), {});
