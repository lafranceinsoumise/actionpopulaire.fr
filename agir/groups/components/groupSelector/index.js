import onDOMReady from "@agir/lib/onDOMReady";

import GroupSelector from "./GroupSelector";
import { getStatefulRenderer } from "@agir/lib/utils/react";

const getInitial = field =>
  field.selectedIndex !== -1 && field.value
    ? {
        id: field.options[field.selectedIndex].value,
        name: field.options[field.selectedIndex].label
      }
    : null;

const getProps = field => ({
  groupChoices: Array.from(field.options)
    .filter(option => option.value)
    .map(option => ({
      id: option.value,
      name: option.label
    })),
  defaultOptionsLabel: field.dataset.defaultOptionsLabel || undefined
});

const getValue = value => (value ? value.id : "");

const selector = 'select[data-group-selector="Y"]';

const renderer = getStatefulRenderer(GroupSelector, selector, {
  getInitial,
  getProps,
  getValue
});

onDOMReady(renderer);
