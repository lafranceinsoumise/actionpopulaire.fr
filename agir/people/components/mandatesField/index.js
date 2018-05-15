import React from 'react';
import ReactDOM from 'react-dom';

import MandatesField from './mandatesField';

const render = (hiddenField, element) => {
  ReactDOM.render(
    <MandatesField hiddenField={hiddenField}/>,
    element
  );
};

const onLoad = function () {
  const hiddenField = document.querySelector('input[name="mandates"]');

  if (hiddenField && !document.getElementById('mandatesControl')) {
    const insertingNode = document.createElement('div');
    insertingNode.id = 'mandatesControl';
    hiddenField.type = 'hidden';
    hiddenField.parentNode.appendChild(insertingNode);
    render(hiddenField, insertingNode);
  }
};

setImmediate(onLoad);

document.addEventListener('turbolinks:load', onLoad);
