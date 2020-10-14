import React from "react";
import ReactDOM from "react-dom";
import Header from "../genericComponents/Header";

const headerProps = JSON.parse(
  document.getElementById("headerProps").textContent
);

const showHeader = () => {
  ReactDOM.render(
    <Header {...headerProps} />,
    document.getElementById("header")
  );
};
document.addEventListener("turbolinks:load", showHeader);
