import React from "react";
import ReactDOM from "react-dom";

import NotificationsCenter from "./NotificationsCenter";
import moment from "moment";
import "moment/locale/fr";

moment.locale("fr");

window.setUpNotificationsCenter = function(element, notifications) {
  ReactDOM.render(
    <NotificationsCenter notifications={notifications} />,
    element
  );
};
