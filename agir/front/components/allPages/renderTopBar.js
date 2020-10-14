import React from "react";
import ReactDOM from "react-dom";
import TopBar from "./TopBar";

const headerProps = JSON.parse(
  document.getElementById("headerProps").textContent
);

const showHeader = () => {
  ReactDOM.render(
    <TopBar {...headerProps} />,
    document.getElementById("top-bar")
  );
};
document.addEventListener("turbolinks:load", showHeader);
