import 'react-hot-loader/patch';
import React from 'react';
import ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';

import './style.css';

import CreateGroupForm from './createGroupForm';
import CreateEventForm from './createEventForm';

const render = Component => {
  ReactDOM.render(
    <AppContainer>
      <Component />
    </AppContainer>,
    document.getElementById('create-group-react-app')
  );
};

const renderForm = (Component, file) => () => {
  if (module.hot) {
    module.hot.accept(file, () => {
      const Component = require(file).default;
      render(Component);
    });
  }

  render(Component);
};

export const createGroupForm = renderForm(CreateGroupForm, './createGroupForm.js');
export const createEventForm = renderForm(CreateEventForm, './createEventForm.js');
