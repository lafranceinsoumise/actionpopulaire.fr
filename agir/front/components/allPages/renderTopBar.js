import React from "react";
import ReactDOM from "react-dom";
import TopBar from "./TopBar";
import { ConfigProvider } from "../genericComponents/Config";

const showHeader = () => {
  ReactDOM.render(
    <ConfigProvider>
      <TopBar />
    </ConfigProvider>,
    document.getElementById("top-bar")
  );
};
document.addEventListener("turbolinks:load", showHeader);
