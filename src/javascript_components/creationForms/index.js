import React from 'react';
import ReactDOM from 'react-dom';
import 'babel-polyfill';

import './style.css';

import CreateGroupForm from './createGroupForm';
import CreateEventForm from './createEventForm';

const render = (Component) => (id, props = {}) => {
  ReactDOM.render(
    <Component {...props} />,
    document.getElementById(id)
  );
};

export const renderCreateEventForm = render(CreateEventForm);
export const renderCreateGroupForm = render(CreateGroupForm);
