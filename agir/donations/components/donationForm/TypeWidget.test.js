import React from "react";
import { render, fireEvent, cleanup } from "@testing-library/react";
import TypeWidget from "@agir/donations/donationForm/TypeWidget";

afterEach(cleanup);

const typeChoices = [
  { value: "S", label: "une seule fois" },
  { value: "M", label: "tous les mois" }
];

test("TypeWidget a bien les boutons", () => {
  const component = render(<TypeWidget typeChoices={typeChoices} />);
  const buttons = component.getAllByRole("button");

  expect(buttons.map(b => b.textContent)).toEqual(
    typeChoices.map(t => t.label)
  );
});

test("TypeWidget style le bouton quand c'est sélectionné", () => {
  const component = render(<TypeWidget typeChoices={typeChoices} type={"S"} />);
  expect(component.getByText("une seule fois").classList).toContain(
    "btn-primary"
  );
  expect(component.getByText("tous les mois").classList).toContain(
    "btn-default"
  );
});

test("TypeWidget réagit quand on clique", () => {
  let currentType = null;
  const component = render(
    <TypeWidget
      typeChoices={typeChoices}
      onTypeChange={t => (currentType = t)}
    />
  );

  const button = component.getByText("tous les mois");
  fireEvent.click(button);
  expect(currentType).toBe("M");
});
