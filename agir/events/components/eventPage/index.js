import React from "react";
import ReactDom from "react-dom";

import { GlobalContextProvider } from "@agir/front/genericComponents/GobalContext";
import EventPage from "./EventPage";

const render = () => {
  const data = JSON.parse(document.getElementById("exportedEvent").textContent);
  ReactDom.render(
    <GlobalContextProvider>
      <EventPage {...data} />
    </GlobalContextProvider>,
    document.getElementById("mainApp")
  );
};

document.addEventListener("turbolinks:load", render);
