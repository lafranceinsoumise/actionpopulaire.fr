// Return string from @amount given in centimes. Example : 3050 => 30,5€
export const displayAmount = (amount) =>
  parseInt(amount / 100) + "," + (amount % 100) + "€";
