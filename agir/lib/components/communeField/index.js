import "core-js/stable";
import "regenerator-runtime/runtime";
import onDOMReady from "@agir/lib/utils/onDOMReady";

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
    } catch (e) {
      /* Rien à faire ici */
    }
  }
  return props;
};

(async function () {
  const [
    { default: CommuneField },
    { getStatefulRenderer },
  ] = await Promise.all([
    import("./CommuneField"),
    import("@agir/lib/utils/react"),
  ]);

  const renderer = getStatefulRenderer(CommuneField, selector, {
    getInitial,
    getProps,
  });

  onDOMReady(renderer);
})();
