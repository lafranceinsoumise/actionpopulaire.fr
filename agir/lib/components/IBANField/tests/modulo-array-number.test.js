import {
  arrayNumberModulo,
  strToArrayNumber,
} from "@agir/lib/IBANField/validation";

test("strToArrayNumber", () => {
  expect(strToArrayNumber("0", 1)).toEqual([0]);
  expect(strToArrayNumber("1337", 4)).toEqual([1337]);
  expect(strToArrayNumber("123456789", 1)).toEqual([9, 8, 7, 6, 5, 4, 3, 2, 1]);
  expect(strToArrayNumber("11110000", 4)).toEqual([0, 1111]);
  expect(
    strToArrayNumber("9999888877776666555544443333222211110000", 4),
  ).toEqual([0, 1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999]);
});

test("La fonction modulo sur des nombres contenues dans un array", () => {
  const strNumbers = [
    "0",
    "1",
    "9",
    "86",
    "869",
    "78947",
    "10000000",
    "12356489",
    "9876543210",
  ];
  const maxPowTen = 8;
  const modulos = [1, 2, 5, 7, 27, 41, 32, 53, 48, 96, 97, 100, 562, 1992];
  for (let powTen = 1; powTen <= maxPowTen; powTen++) {
    for (let j = 0; j < modulos.length; j++) {
      for (let k = 0; k < strNumbers.length; k++) {
        const strNbr = strNumbers[k];
        const nbr = parseInt(strNbr);
        const arrayNbr = strToArrayNumber(strNbr, powTen);
        const modulo = modulos[j];

        const modArray = arrayNumberModulo(arrayNbr, powTen, modulo);
        const modNbr = nbr % modulo;

        expect(modNbr).toBe(modArray);
      }
    }
  }
});
