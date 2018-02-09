import 'react-hot-loader/patch';
import React from 'react';
import ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';

import './style.css';

import CreateGroupForm from './createGroupForm';
import CreateEventForm from './createEventForm';

const render = (Component, id) => {
  ReactDOM.render(
    <AppContainer>
      <Component />
    </AppContainer>,
    document.getElementById(id)
  );
};

if (module.hot) {
  module.hot.accept('./createGroupForm.js', () => {
    const CreateGroupForm = require('./createGroupForm.js').default;
    render(CreateGroupForm, 'create-group-react-app');
  });
  module.hot.accept('./createEventForm.js', () => {
    const CreateEventForm = require('./createEventForm.js').default;
    render(CreateEventForm, 'create-event-react-app');
  });
}

export const createGroupForm = () => render(CreateGroupForm, 'create-group-react-app');
export const createEventForm = () => render(CreateEventForm, 'create-event-react-app');
