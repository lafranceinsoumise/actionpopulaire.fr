import onDOMReady from "@agir/lib/utils/onDOMReady";

const getInitial = (field) =>
  field.selectedIndex !== -1 && field.value
    ? {
        id: field.options[field.selectedIndex].value,
        name: field.options[field.selectedIndex].label,
      }
    : null;

const getProps = (field) => ({
  groupChoices: Array.from(field.options)
    .filter((option) => option.value)
    .map((option) => ({
      id: option.value,
      name: option.label,
    })),
  defaultOptionsLabel: field.dataset.defaultOptionsLabel || undefined,
});

const valueToString = (value) => (value ? value.id : "");

const selector = 'select[data-group-selector="Y"]';

(async function () {
  const [{ default: GroupSelector }, { getStatefulRenderer }] = Promise.all([
    import("./GroupSelector"),
    import("@agir/lib/utils/react"),
  ]);
  const renderer = getStatefulRenderer(GroupSelector, selector, {
    getInitial,
    getProps,
    valueToString,
  });

  onDOMReady(renderer);
})();
