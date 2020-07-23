import { isIBANValid } from "@agir/lib/IBANField/validation";

const GOOD_IBANS = [
  "NL28ABNA4217631642",
  "MZ65681166912998238935942",
  "SE12 3194 9817 7433 1622 1177",
  "FR3130066119293675223821795",
  "BA93 1022 2516 3726 3927",
];

const BAD_IBANS = [
  "SE12 3194 9817 1234 1622 1177",
  "78923798274982798",
  "298902 JOII 2IJOJIO23",
  "1234",
  "FR7612345678901276327382893289283923898290382",
];

test("Identifie des IBAN valides", () => {
  for (let iban of GOOD_IBANS) {
    expect(isIBANValid(iban)).toBe(true);
  }
});

test("Identifie des IBAN invalides", () => {
  for (let iban of BAD_IBANS) {
    expect(isIBANValid(iban)).toBe(false);
  }
});
