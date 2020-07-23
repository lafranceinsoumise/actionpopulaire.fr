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
  maxAmount
) => {
  const newState = oldState.slice();
  newState[groupIndex] = { ...oldState[groupIndex], amount: newValue };

  if (newValue <= oldState[groupIndex]) {
    return newState;
  }

  const newTotal = maxAmount - totalAllocatedFromState(newState);

  if (newTotal >= 0) {
    return newState;
  }

  allocations[groupIndex] = 0;

  const allocations = newState.map(({ amount }) => amount);
  const newAllocations = dealFromWeights(allocations, maxAmount - newValue);
  newAllocations[groupIndex] = newValue;
  return newAllocations.map((amount, i) => ({ ...oldState[i], amount }));
};

export const totalAllocatedFromState = (state) =>
  state.reduce((acc, alloc) => acc + alloc.amount, 0);
