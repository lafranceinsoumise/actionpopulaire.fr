import React from 'react';
import ReactDOM from 'react-dom';

import AmountWidget from './AmountWidget';

const render = (name, element) => {
  ReactDOM.render(
    <AmountWidget name={name}/>,
    element
  );
};

const onLoad = function () {
  const inputs = document.querySelectorAll('input.amountwidget');

  for (let input of inputs) {
    const insertingNode = document.createElement('div');
    input.parentNode.appendChild(insertingNode);
    const name = input.name;
    input.remove();
    render(name, insertingNode);
  }
};

setImmediate(onLoad);
document.addEventListener('turbolinks:load', onLoad);
