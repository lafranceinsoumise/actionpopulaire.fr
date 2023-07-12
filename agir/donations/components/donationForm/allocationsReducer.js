import { dealFromWeights, sum } from "@agir/lib/utils/math";

export const changeTotalAmount = (oldState, oldTotal, newTotal) => {
  const oldAllocations = oldState.map((alloc) => alloc.amount);
  oldAllocations.push(oldTotal - sum(oldAllocations));
  return dealFromWeights(oldAllocations, newTotal)
    .slice(0, oldState.length)
    .map((amount, i) => ({
      ...oldState[i],
      amount,
    }));
};

export const changeUnallocatedAmount = (oldState, newTotal) => {
  const oldAllocations = oldState.map((alloc) => alloc.amount);
  return dealFromWeights(oldAllocations, newTotal).map((amount, i) => ({
    ...oldState[i],
    amount,
  }));
};

export const changeSingleGroupAllocation = (
  oldState,
  groupIndex,
  newValue,
  maxAmount,
) => {
  const totalAllocated = oldState.reduce((acc, alloc) => acc + alloc.amount, 0);
  const maxAmountForThisGroup =
    maxAmount - totalAllocated + oldState[groupIndex].amount;

  const newState = oldState.slice();
  newState[groupIndex] = {
    ...oldState[groupIndex],
    amount: Math.min(newValue, maxAmountForThisGroup),
  };
  return newState;
};

export const totalAllocatedFromState = (state) =>
  state.reduce((acc, alloc) => acc + alloc.amount, 0);
