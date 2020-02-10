import { formatInputContent } from "@agir/lib/IBANField/validation";

test("Le format se fait correctement", () => {
  expect(formatInputContent("ABCD1234", 0)).toEqual({
    value: "ABCD 1234",
    cursor: 0
  });

  expect(formatInputContent("aBcD 1245", 2)).toEqual({
    value: "ABCD 1245",
    cursor: 2
  });

  expect(formatInputContent("1234-32", 5)).toEqual({
    value: "1234 32",
    cursor: 5
  });

  expect(formatInputContent("123456", 5)).toEqual({
    value: "1234 56",
    cursor: 6
  });
});

test("Les cas limites pour le curseur sont correctement gérés", () => {
  expect(formatInputContent("12345678", 8)).toEqual({
    value: "1234 5678",
    cursor: 9
  });

  expect(formatInputContent("1234 ", 5)).toEqual({
    value: "1234",
    cursor: 4
  });
});
