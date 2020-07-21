import onDOMReady from "@agir/lib/onDOMReady";

import CommuneField from "./CommuneField";
import { getStatefulRenderer } from "@agir/lib/utils/react";

const getInitial = (field) =>
  field.value
    ? {
        value: field.value,
        label: field.dataset.label,
      }
    : null;
const selector = 'input[data-commune="Y"]';

const getProps = (field) => {
  const props = {};
  if (field.dataset.types) {
    try {
      const types = JSON.parse(field.dataset.types);
      if (Array.isArray(types)) {
        props.types = types;
      }
    } catch (e) {}
  }
  return props;
};

const renderer = getStatefulRenderer(CommuneField, selector, {
  getInitial,
  getProps,
});

onDOMReady(renderer);
