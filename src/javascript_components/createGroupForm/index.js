import 'react-hot-loader/patch';
import React from "react";
import ReactDOM from "react-dom";
import { AppContainer } from 'react-hot-loader';


import CreateGroupForm from './createGroupForm.js';

const render = Component => {
  ReactDOM.render(
    <AppContainer>
      <Component />
    </AppContainer>,
    document.getElementById('create-group-react-app')
  );
};

if (module.hot) {
  module.hot.accept('./createGroupForm.js', () => {
    const CreateGroupForm = require('./createGroupForm.js').default;
    render(CreateGroupForm);
  });
}

render(CreateGroupForm);