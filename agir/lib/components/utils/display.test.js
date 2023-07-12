import { GENDER, getGenderedWord } from "./display";

describe("agir.lib.utils.display", function () {
  describe("getGenderedWord function", function () {
    const testCases = [
      {
        args: [],
        expected: "",
      },
      {
        args: [GENDER.other, 12345],
        expected: "",
      },
      {
        args: [null, "Insoumis·e"],
        expected: "Insoumis·e",
      },
      {
        args: ["not" + GENDER.female, "Insoumis·e"],
        expected: "Insoumis·e",
      },
      {
        args: [GENDER.other, "Insoumis·e"],
        expected: "Insoumis·e",
      },
      {
        args: [GENDER.female, "Insoumis·e", "Insoumise", "Insoumis"],
        expected: "Insoumise",
      },
      {
        args: [GENDER.male, "Insoumis·e", "Insoumise", "Insoumis"],
        expected: "Insoumis",
      },
      {
        args: [GENDER.other, "Insoumis·e", "Insoumise", "Insoumis"],
        expected: "Insoumis·e",
      },
      {
        args: [GENDER.female, "Insoumis·e"],
        expected: "Insoumise",
      },
      {
        args: [GENDER.male, "Insoumis⋅e"],
        expected: "Insoumis",
      },
      {
        args: [GENDER.female, "Insoumis·es"],
        expected: "Insoumises",
      },
      {
        args: [GENDER.male, "Insoumis·es"],
        expected: "Insoumis",
      },
      {
        args: [GENDER.female, "ÉLU·ES"],
        expected: "ÉLUES",
      },
      {
        args: [GENDER.male, "ÉLU·ES"],
        expected: "ÉLUS",
      },
      {
        args: [GENDER.female, "heureux·ses"],
        expected: "heureux·ses",
      },
      {
        args: [GENDER.male, "heureux·ses"],
        expected: "heureux·ses",
      },
    ];
    testCases.forEach(({ args, expected }) => {
      it(`It should return "${expected}" with arguments (${args.join(
        ",",
      )})`, function () {
        const result = getGenderedWord(...args);
        expect(result).toEqual(expected);
      });
    });
  });
});
