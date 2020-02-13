import "core-js/stable";
import "regenerator-runtime/runtime";
import React from "react";
import ReactDOM from "react-dom";

import "./style.css";

import CreateGroupForm from "./createGroupForm";
import CreateEventForm from "./createEventForm";

const render = Component => (id, props = {}) => {
  ReactDOM.render(<Component {...props} />, document.getElementById(id));
};

const renderCreateEventForm = render(CreateEventForm);
const renderCreateGroupForm = render(CreateGroupForm);

function onLoad() {
  const reactJsonScript = document.getElementById("react-json-script");
  let reactAppProps = null;
  if (reactJsonScript && reactJsonScript.type === "application/json") {
    reactAppProps = JSON.parse(reactJsonScript.textContent);
  }

  if (document.getElementById("create-event-react-app")) {
    renderCreateEventForm("create-event-react-app", reactAppProps || {});
  }

  if (document.getElementById("create-group-react-app")) {
    renderCreateGroupForm("create-group-react-app", reactAppProps || {});
  }
}

document.addEventListener("turbolinks:load", onLoad);
