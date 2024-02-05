import React from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";
import DonationForm from "@agir/donations/donationForm/DonationForm";
import { renderReactComponent } from "@agir/lib/utils/react";

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
          label: options[i].label,
        },
        choiceAttrs ? choiceAttrs[i] || {} : {},
      ),
    );
  }

  return choices;
}

const replaceForm = (selector) => {
  const form = document.querySelector(selector);
  if (!form) {
    return;
  }
  const props = { initial: {} };

  const typeSelect = form.querySelector('select[name="type"]');
  if (typeSelect) {
    props.typeChoices = getChoices(typeSelect);
    typeSelect.parentNode.removeChild(typeSelect);
  }

  props.enableAllocations = false;
  const allocationsInput = form.querySelector('input[name="allocations"]');
  if (allocationsInput) {
    props.enableAllocations = true;
    props.groupChoices = allocationsInput.dataset.choices
      ? JSON.parse(allocationsInput.dataset.choices)
      : [];
    props.initial.allocations = allocationsInput.value
      ? JSON.parse(allocationsInput.value)
      : [];

    allocationsInput.parentNode.removeChild(allocationsInput);
  }

  const amountLabel = form.querySelector('label[for="id_amount"]');
  if (amountLabel && amountLabel.textContent.includes("prêt")) {
    props.typeActe = "mon prêt";
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
  amountInput.parentNode.removeChild(amountInput);

  // pour tous les champs hidden restant, on les transmet tels quels
  props.hiddenFields = {};
  Array.from(form.querySelectorAll('input[type="hidden"]')).forEach((input) => {
    props.hiddenFields[input.name] = input.value;
  });

  const reactDiv = document.createElement("div");
  form.parentNode.insertBefore(reactDiv, form);
  form.parentNode.removeChild(form);
  // remove all children of the form

  renderReactComponent(<DonationForm {...props} />, reactDiv);
};

onDOMReady(() => replaceForm("form.donation-form"));
