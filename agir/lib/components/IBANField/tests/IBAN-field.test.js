/**
 * @jest-environment jsdom
 */

import React from "react";
import { render, fireEvent, cleanup } from "@testing-library/react";

import IBANField from "../IBAN-field";
import { isIBANValid } from "@agir/lib/IBANField/validation";

afterEach(cleanup);

test("Render IBANField", () => {
  const component = render(
    <IBANField id="id_iban" name="iban" placeholder={"mon placeholder"} />,
  );

  const input = component.getByRole("textbox");

  expect(input.id).toBe("id_iban");
  expect(input.name).toBe("iban");
  expect(input.placeholder).toBe("mon placeholder");
});

test("Entrer une donnée mal formatée", () => {
  const placeHolder = "Entrez votre IBAN.";
  const input = render(
    <IBANField placeholder={placeHolder} />,
  ).getByPlaceholderText(placeHolder);
  fireEvent.change(input, {
    target: { value: "  abc   ;:,:;:! 'éDEF çàèçè--0123" },
  });
  expect(input.value).toBe("ABCD EF01 23");
});

test("Un IBAN d'une nationalité non accepté", () => {
  const placeHolder = "Entrez votre IBAN.";
  const iban = render(
    <IBANField allowedCountries={["FR"]} placeholder={placeHolder} />,
  );
  const input = iban.getByRole("textbox");
  fireEvent.change(input, {
    target: { value: "EN1234567890" },
  });
  fireEvent.blur(input);
  const wrongCountry = iban.getByText(
    "La nationalité de cet IBAN n'est pas acceptée.",
  );
  expect(wrongCountry).toBeInstanceOf(HTMLSpanElement);
});

test("Un IBAN invalide", () => {
  const placeHolder = "Entrez votre IBAN.";
  const iban = render(
    <IBANField allowedCountry={["FR"]} placeholder={placeHolder} />,
  );
  const input = iban.getByPlaceholderText(placeHolder);
  fireEvent.change(input, {
    target: { value: "FR8439084093843098490309843908" },
  });

  fireEvent.blur(input);
  let invalid = iban.queryByText("Cet IBAN est invalide.");
  expect(invalid).toBeDefined();

  fireEvent.focus(input);
  invalid = iban.queryByText("Cet IBAN est invalide.");
  expect(invalid).toBeNull();
});

test("Le refus d'IBANs invalides", () => {
  // on Prend un IBAN valid en reference
  expect(isIBANValid("FR7630001007941234567890185")).toBe(true);
  for (let i = 1; i < 97; i++) {
    const nbr = (76 + i) % 100;
    const validationKey = (nbr < 10 ? "0" : "") + String(nbr);
    const iban = "FR" + validationKey + "30001007941234567890185";
    expect(isIBANValid(iban)).toBe(false);
  }
});
