import React from "react";
import ReactDOM from "react-dom";

import DonationForm from "./DonationForm";

const render = (widget, element) => {
  ReactDOM.render(widget, element);
};

function getChoices(select) {
  const options = select.options;
  const choices = [];
  let choiceAttrs = null;

  try {
    if (select.dataset.choiceAttrs) {
      choiceAttrs = JSON.parse(select.dataset.choiceAttrs);
    }
    // eslint-disable-next-line no-empty
  } catch (e) {}

  for (let i = 0; i < options.length; i++) {
    choices.push(
      Object.assign(
        {
          value: options[i].value,
          label: options[i].label
        },
        choiceAttrs ? choiceAttrs[i] || {} : {}
      )
    );
  }

  return choices;
}

const replaceForm = selector => {
  const form = document.querySelector(selector);
  const props = { initial: {} };

  const typeSelect = form.querySelector('select[name="type"]');
  if (typeSelect) {
    props.typeChoices = getChoices(typeSelect);
    typeSelect.remove();
  }

  const allocationsInput = form.querySelector('input[name="allocations"]');
  if (allocationsInput) {
    props.groupChoices = allocationsInput.dataset.choices
      ? JSON.parse(allocationsInput.dataset.choices)
      : [];
    props.initial.allocations = allocationsInput.value
      ? JSON.parse(allocationsInput.value)
      : [];

    allocationsInput.remove();
  }

  const amountInput = form.querySelector('input[name="amount"]');
  props.minAmount = parseFloat(amountInput.min);
  props.maxAmount = parseFloat(amountInput.max);
  props.minAmountError = amountInput.dataset.minAmountError;
  props.maxAmountError = amountInput.dataset.maxAmountError;
  props.amountChoices = amountInput.dataset.amountChoices
    ? JSON.parse(amountInput.dataset.amountChoices)
    : null;
  props.showTaxCredit = !amountInput.dataset.hideTaxCredit;
  props.initial.amount = +amountInput.value || null;
  amountInput.remove();

  // pour tous les champs hidden restant, on les transmet tels quels
  props.hiddenFields = {};
  Array.from(form.querySelectorAll('input[type="hidden"]')).forEach(input => {
    props.hiddenFields[input.name] = input.value;
  });

  const reactDiv = document.createElement("div");
  form.parentNode.insertBefore(reactDiv, form);
  form.remove();
  // remove all children of the form

  render(<DonationForm {...props} />, reactDiv);
};

const onLoad = function() {
  replaceForm("form.donation-form");
};

document.addEventListener("turbolinks:load", onLoad);
