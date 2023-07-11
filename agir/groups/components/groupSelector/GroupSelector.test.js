/**
 * @jest-environment jsdom
 */
import React from "react";

import { act, cleanup, fireEvent, render } from "@testing-library/react";

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
    <GroupSelector groupChoices={choices} onChange={setLastValue} />,
  );

  // il existe un faux éléments placeholder
  component.getByText("Choisissez un groupe...");

  const input = component.getByRole("combobox");
  expect(input.value).toEqual("");

  fireEvent.focus(input);
  fireEvent.keyDown(input, { key: "ArrowDown", code: "ArrowDown" });

  component.getByText("Groupe 1");
  component.getByText("Groupe 2");

  fireEvent.keyDown(input, { key: "Enter", code: "Enter" });

  expect(lastValue).toEqual(choices[0]);
});

test("Recherche simple dans GroupSelector", async () => {
  const promise = Promise.resolve([{ id: "3", name: "Groupe 3" }]);
  const search = jest.fn(() => promise);
  const component = render(<GroupSelector groupChoices={[]} search={search} />);
  const input = component.getByRole("combobox");
  expect(search.mock.calls).toHaveLength(0);
  fireEvent.input(input, { target: { value: "try" } });
  expect(search.mock.calls).toHaveLength(1);
  expect(search.mock.calls[0][0]).toEqual("try");
  await act(() => promise);
  component.getByText("Groupe 3");
});
