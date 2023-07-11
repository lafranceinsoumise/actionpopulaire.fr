export const sum = (array) => array.reduce((a, b) => a + b, 0);

export const maxIndex = (array) =>
  array.reduce((iMax, x, i, array) => (array[iMax] < x ? i : iMax), 0);

export const dealFromWeights = (weights, newTotal) => {
  let weightSum = sum(weights);

  if (weightSum === 0) {
    // on élimine ce cas pathologique en assignant les mêmes poids à tous !
    weights = weights.map(() => 1);
    weightSum = weights.length;
  }

  const newDeal = weights.map((weight) =>
    Math.floor((weight * newTotal) / weightSum),
  );

  newTotal -= newDeal.reduce((a, b) => a + b, 0);

  while (newTotal > 0) {
    const averages = weights.map((r, i) => r / (newDeal[i] + 1));
    newDeal[maxIndex(averages)]++;
    newTotal--;
  }

  return newDeal;
};
