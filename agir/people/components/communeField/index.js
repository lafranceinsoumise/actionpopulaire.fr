import onDOMReady from "@agir/lib/onDOMReady";

import CommuneField from "./CommuneField";
import { getStatefulRenderer } from "@agir/lib/utils/react";

const getInitial = field =>
  field.value
    ? {
        value: field.value,
        label: field.dataset.label
      }
    : null;
const selector = 'input[data-commune="Y"]';

const renderer = getStatefulRenderer(CommuneField, selector, { getInitial });

onDOMReady(renderer);
