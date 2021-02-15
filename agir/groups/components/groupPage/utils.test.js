import { getGroupTypeWithLocation } from "./utils";

describe("agir.groups.groupPage.utils", function () {
  describe("getGroupTypeWithLocation", function () {
    it("should return arg type if location.zip is falsy", function () {
      const groupType = "Groupe local";
      let result = getGroupTypeWithLocation(groupType, null);
      expect(result).toEqual(groupType);
      result = getGroupTypeWithLocation(groupType, { zip: null });
      expect(result).toEqual(groupType);
    });
    it("should return arg type and zip if location.city and commune.nameOf are falsy", function () {
      const groupType = "Groupe local";
      const location = { zip: "75019" };
      const expected = `${groupType} (${location.zip})`;
      const result = getGroupTypeWithLocation(groupType, location);
      expect(result).toEqual(expected);
    });
    it("should return arg type, zip and city if commune.nameOf is falsy", function () {
      const groupType = "Groupe local";
      const location = { zip: "75019", city: "Paris" };
      const expected = `${groupType} à ${location.city} (${location.zip})`;
      let result = getGroupTypeWithLocation(groupType, location, null);
      expect(result).toEqual(expected);
      result = getGroupTypeWithLocation(groupType, location, { nameOf: null });
    });
    it("should return arg type, zip and modified nameOf if commune.nameOf is truthy", function () {
      let expected = "XXXXX à Bois-d'Arcy (XXXXX)";
      let result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "de Bois-d'Arcy" }
      );
      expect(result).toEqual(expected);
      expected = "XXXXX à Aubervilliers (XXXXX)";
      result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "d'Aubervilliers" }
      );
      expect(result).toEqual(expected);
      expected = "XXXXX au Havre (XXXXX)";
      result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "du Havre" }
      );
      expect(result).toEqual(expected);
      expected = "XXXXX à la Loupe (XXXXX)";
      result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "de la Loupe" }
      );
      expect(result).toEqual(expected);
      expected = "XXXXX aux Lilas (XXXXX)";
      result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "des Lilas" }
      );
      expect(result).toEqual(expected);
      expected = "XXXXX à l'Arbresle (XXXXX)";
      result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "de l'Arbresle" }
      );
      expect(result).toEqual(expected);
      expected = "XXXXX à las Vegas (XXXXX)";
      result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "de las Vegas" }
      );
      expect(result).toEqual(expected);
      expected = "XXXXX à los Angeles (XXXXX)";
      result = getGroupTypeWithLocation(
        "XXXXX",
        { zip: "XXXXX" },
        { nameOf: "de los Angeles" }
      );
      expect(result).toEqual(expected);
    });
  });
});
