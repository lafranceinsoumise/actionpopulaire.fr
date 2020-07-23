import "core-js/stable";
import "regenerator-runtime/runtime";
import React from "react";
import ReactDOM from "react-dom";

import NotificationsCenter from "./NotificationsCenter";

export const setUpNotificationsCenter = function (element, notifications) {
  ReactDOM.render(
    <NotificationsCenter notifications={notifications} />,
    element
  );
};
