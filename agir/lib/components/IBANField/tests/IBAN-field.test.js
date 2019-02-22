import React from "react";
import { render, fireEvent, cleanup } from "react-testing-library";
import renderer from "react-test-renderer";

import { IBANField, isIbanValid } from "../IBAN-field";

afterEach(cleanup);

test("Render IBANField", () => {
  const tree = renderer
    .create(<IBANField placeholder={"Entrez votre IBAN."} />)
    .toJSON();
  expect(tree).toMatchSnapshot();
});

test("Entrer une donnée mal formatée", () => {
  const placeHolder = "Entrez votre IBAN.";
  const input = render(
    <IBANField placeholder={placeHolder} />
  ).getByPlaceholderText(placeHolder);
  fireEvent.change(input, {
    target: { value: "  abc   ;:,:;:! 'éDEF çàèçè--0123" }
  });
  expect(input.value).toBe("ABCD EF01 23");
});

test("Un IBAN d'une nationalité non accepté", () => {
  const placeHolder = "Entrez votre IBAN.";
  const iban = render(
    <IBANField allowedCountry={["FR"]} placeholder={placeHolder} />
  );
  const input = iban.getByPlaceholderText(placeHolder);
  fireEvent.blur(input);
  const wrongCountry = iban.getByText(
    "La nationalité de cet IBAN n'est pas acceptée."
  );
  expect(wrongCountry).toBeInstanceOf(HTMLSpanElement);
});

test("Un IBAN invalide", () => {
  const placeHolder = "Entrez votre IBAN.";
  const iban = render(
    <IBANField allowedCountry={["FR"]} placeholder={placeHolder} />
  );
  const input = iban.getByPlaceholderText(placeHolder);
  fireEvent.blur(input);
  const invalid = iban.getByText("Cet IBAN est invalide.");
  expect(invalid).toBeInstanceOf(HTMLSpanElement);
});

test("Supressions des erreurs quand on focus sur le champ", () => {
  const placeHolder = "Entrez votre IBAN.";
  const iban = render(
    <IBANField
      allowedCountry={["FR"]}
      placeholder={placeHolder}
      errorMessages={{ wrongCountry: "toMatchQuery", invalid: "toMatchQuery" }}
    />
  );
  const input = iban.getByPlaceholderText(placeHolder);
  fireEvent.blur(input);
  let spans = iban.queryAllByText("toMatchQuery");
  expect(spans).toHaveLength(2);
  fireEvent.focus(input);
  spans = iban.queryAllByText("toMachQuery");
  expect(spans).toHaveLength(0);
});

test("Le refus d'IBANs invalides", () => {
  // on Prend un IBAN valid en reference
  expect(isIbanValid("FR7630001007941234567890185")).toBe(true);
  for (let i = 1; i < 97; i++) {
    const nbr = (76 + i) % 100;
    const validationKey = (nbr < 10 ? "0" : "") + String(nbr);
    const iban = "FR" + validationKey + "30001007941234567890185";
    expect(isIbanValid(iban)).toBe(false);
  }
});
