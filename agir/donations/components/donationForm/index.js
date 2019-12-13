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

  props.hiddenFields = Array.from(
    form.querySelectorAll('input[type="hidden"]')
  ).reduce((s, f) => {
    s[f.name] = f.value;
    return s;
  }, {});

  const typeSelect = form.querySelector('select[name="type"]');
  if (typeSelect) {
    props.typeChoices = getChoices(typeSelect);
  }

  const allocationsInput = form.querySelector('input[name="allocations"]');
  if (allocationsInput) {
    props.groupChoices = allocationsInput.dataset.choices
      ? JSON.parse(allocationsInput.dataset.choices)
      : [];
    props.initial.allocations = allocationsInput.value
      ? JSON.parse(allocationsInput.value)
      : [];
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
  props.byMonth = typeof amountInput.dataset.byMonth !== "undefined";
  props.initial.amount = +amountInput.value || null;

  const submitInput = form.querySelector('input[type="submit"]');
  props.buttonLabel = submitInput.value;

  // remove all children of the form
  while (form.firstChild) {
    form.removeChild(form.firstChild);
  }

  render(<DonationForm {...props} />, form);
};

const onLoad = function() {
  replaceForm("form.donation-form");
};

document.addEventListener("turbolinks:load", onLoad);
