import React from 'react';
import ReactDOM from 'react-dom';

import AmountWidget from './AmountWidget';

const render = (hiddenField, element) => {
  ReactDOM.render(
    <AmountWidget hiddenField={hiddenField}/>,
    element
  );
};

const onLoad = function () {
  const hiddenFields = document.querySelectorAll('input.amountwidget');

  for (let hiddenField of hiddenFields) {
    if (!hiddenField.classList.contains('reactified')) {
      hiddenField.classList.add('reactified');
      hiddenField.disabled = true;

      const insertingNode = document.createElement('div');
      hiddenField.parentNode.appendChild(insertingNode);
      render(hiddenField, insertingNode);
    }
  }
};

setImmediate(onLoad);
document.addEventListener('turbolinks:load', onLoad);
