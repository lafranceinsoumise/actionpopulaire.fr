/**
 * @jest-environment jsdom
 */

import React from "react";
import { render, fireEvent, cleanup } from "@testing-library/react";
import TypeWidget from "@agir/donations/donationForm/TypeWidget";

afterEach(cleanup);

const typeChoices = [
  { value: "S", label: "une seule fois" },
  { value: "M", label: "tous les mois" },
];

test("TypeWidget style le bouton quand c'est sélectionné", () => {
  const component = render(<TypeWidget typeChoices={typeChoices} type={"S"} />);
  expect(component.getByLabelText("une seule fois")).toBeChecked();
  expect(component.getByLabelText("tous les mois")).not.toBeChecked();
});

test("TypeWidget réagit quand on clique", () => {
  let currentType = null;
  const component = render(
    <TypeWidget
      typeChoices={typeChoices}
      onTypeChange={(t) => (currentType = t)}
    />,
  );

  const input = component.getByLabelText("tous les mois");
  fireEvent.click(input);
  expect(currentType).toBe("M");
});
