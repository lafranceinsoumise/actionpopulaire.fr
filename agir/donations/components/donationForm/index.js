import React from 'react';
import ReactDOM from 'react-dom';

import DonationForm from './DonationForm';


const render = (widget, element) => {
  ReactDOM.render(
    widget,
    element
  );
};

const replaceForm = (selector) => {
  const form = document.querySelector(selector);
  const props = {};

  props.csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

  const groupSelect = form.querySelector('select[name="group"]');

  if (groupSelect) {
    const groupOptions = groupSelect ? groupSelect.options : [];
    props.groupChoices = [];
    for (let i = 0; i < groupOptions.length; i++) {
      props.groupChoices.push({
        value: groupOptions[i].value,
        label: groupOptions[i].label
      });
    }
    props.initialGroup = groupSelect && groupSelect.value;
  } else {
    props.initialGroup = form.dataset.groupId || null;
    props.groupName = form.dataset.groupName || null;
  }

  const amountInput = form.querySelector('input[name="amount"]');
  props.minAmount = parseFloat(amountInput.min);
  props.maxAmount = parseFloat(amountInput.max);

  // remove all children of the form
  while(form.firstChild) {
    form.removeChild(form.firstChild);
  }

  render(
    <DonationForm {...props} />,
    form
  );
};

const onLoad = function () {
  replaceForm('form.donation-form');
};

document.addEventListener('turbolinks:load', onLoad);
