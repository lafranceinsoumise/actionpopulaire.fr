/**
 * @jest-environment jsdom
 */
import React from "react";
import { cleanup, fireEvent, render } from "@testing-library/react";

import AmountWidget from "./AmountWidget";

afterEach(cleanup);

test("AmountWidget dans son état initial", () => {
  const component = render(<AmountWidget />);

  const buttons = component.getAllByRole("button");
  for (let button of buttons) {
    expect(button.textContent).toMatch(/[0-9]+\s*€/);
    expect(button.classList).toContain("btn-unselected");
  }

  expect(component.getByPlaceholderText("Autre montant")).toBeDefined();
});

test("AmountWidget avec un montant sélectionné", () => {
  const component = render(<AmountWidget amount={50 * 100} />);

  const buttons = component.getAllByRole("button");
  for (let button of buttons) {
    expect(button.textContent).toMatch(/[0-9]+\s*€/);
    if (+/([0-9]+)\s*€/.exec(button.textContent)[1] === 50) {
      expect(button.classList).toContain("btn-primary");
    } else {
      expect(button.classList).toContain("btn-unselected");
    }
  }
});

test("Sélectionner des valeurs dans le AmountWidget", () => {
  let currentValue = null;

  const component = render(
    <AmountWidget
      amount={null}
      onAmountChange={(amount) => (currentValue = amount)}
      error={null}
    />,
  );
  // let's click on the 20 € button
  const button50 = component.getByText(/50\s*€/);
  fireEvent.click(button50);
  expect(currentValue).toEqual(50 * 100);

  const input = component.getByPlaceholderText("Autre montant");
  fireEvent.change(input, { target: { value: "23" } });
  expect(currentValue).toEqual(23 * 100);
});

test("utiliser des montants autres que ceux par défaut", () => {
  const choices = [1, 2, 3, 4];
  const component = render(<AmountWidget amountChoices={choices} />);
  const buttons = component.queryAllByText(/[0-9]+\s*€/);

  expect(buttons.map((e) => +/([0-9]+)\s*€/.exec(e.textContent)[1])).toEqual(
    choices,
  );
});
