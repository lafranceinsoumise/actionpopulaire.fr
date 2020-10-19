import React from "react";
import ReactDOM from "react-dom";
import TopBar from "./TopBar";
import { GlobalContextProvider } from "../genericComponents/GobalContext";

const showHeader = () => {
  ReactDOM.render(
    <GlobalContextProvider>
      <TopBar />
    </GlobalContextProvider>,
    document.getElementById("top-bar")
  );
};
document.addEventListener("turbolinks:load", showHeader);
