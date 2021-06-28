/**
 * @jest-environment jsdom
 */
import React from "react";

import { cleanup, fireEvent, render } from "@testing-library/react";

import GroupSelector from "./GroupSelector";

afterEach(cleanup);

test("GroupSelector dans son état initial", () => {
  const choices = [
    { id: "1", name: "Groupe 1" },
    { id: "2", name: "Groupe 2" },
  ];

  let lastValue = null;

  const setLastValue = (v) => {
    lastValue = v;
  };

  const component = render(
    <GroupSelector groupChoices={choices} onChange={setLastValue} />
  );

  // il existe un faux éléments placeholder
  component.getByText("Choisissez un groupe...");

  const input = component.getByRole("textbox"); // input type="text"
  expect(input.value).toEqual("");

  fireEvent.focus(input);
  fireEvent.keyDown(input, { key: "ArrowDown", code: "ArrowDown" });

  component.getByText("Groupe 1");
  component.getByText("Groupe 2");

  fireEvent.keyDown(input, { key: "Enter", code: "Enter" });

  expect(lastValue).toEqual(choices[0]);
});

test("Recherche simple dans GroupSelector", async () => {
  let lastSearch = null;
  let signalAfterSearch = null;

  const afterSearch = new Promise((resolve) => {
    signalAfterSearch = resolve;
  });

  const search = (q) => {
    lastSearch = q;
    setImmediate(signalAfterSearch);
    return Promise.resolve([{ id: "3", name: "Groupe 3" }]);
  };

  const component = render(<GroupSelector groupChoices={[]} search={search} />);

  const input = component.getByRole("textbox"); // input type="text"

  fireEvent.input(input, { target: { value: "try" } });
  expect(lastSearch).toEqual("try");

  await afterSearch;

  component.getByText("Groupe 3");
});
