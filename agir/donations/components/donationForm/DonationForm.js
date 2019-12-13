import { hot } from "react-hot-loader/root"; // doit être importé avant React
import React, { useState } from "react";
import PropTypes from "prop-types";

import Button from "@agir/lib/bootstrap/Button";

import { changeTotalAmount } from "./allocationsReducer";
import AllocationWidget from "./AllocationsWidget";
import AmountWidget from "./AmountWidget";
import TypeWidget from "./TypeWidget";

const DonationForm = ({
  initial,
  typeChoices,
  amountChoices,
  groupChoices,
  hiddenFields,
  minAmount,
  maxAmount,
  minAmountError,
  maxAmountError,
  showTaxCredit,
  buttonLabel,
  byMonth
}) => {
  const [type, setType] = useState(initial.type || null);
  const [allocations, setAllocations] = useState(initial.allocations || {});
  const [amount, setAmount] = useState(initial.amount || null);

  const customError =
    amount === null
      ? null
      : minAmount && amount < minAmount
      ? minAmountError
      : maxAmount && amount > maxAmount
      ? maxAmountError
      : null;

  return (
    <div>
      {Object.keys(hiddenFields).map(k => (
        <input key={k} type="hidden" name={k} value={hiddenFields[k]} />
      ))}
      <input type="hidden" name="type" value={type || ""} />
      <input type="hidden" name="amount" value={amount || ""} />
      <input
        type="hidden"
        name="allocations"
        value={JSON.stringify(allocations.filter(a => a.amount !== 0))}
      />
      {typeChoices && (
        <TypeWidget
          type={type}
          typeChoices={typeChoices}
          onTypeChange={type => {
            setType(type);
            setAmount(null);
            setAllocations(
              allocations.map(({ group }) => ({ group, amount: 0 }))
            );
          }}
        />
      )}
      <AmountWidget
        disabled={type === null}
        amount={amount}
        amountChoices={
          Array.isArray(amountChoices) ? amountChoices : amountChoices[type]
        }
        showTaxCredit={showTaxCredit}
        byMonth={byMonth}
        error={customError}
        onAmountChange={newAmount => {
          setAmount(newAmount);
          setAllocations(changeTotalAmount(allocations, amount, newAmount));
        }}
      />
      {groupChoices && (
        <AllocationWidget
          groupChoices={groupChoices}
          value={allocations}
          onChange={setAllocations}
          maxAmount={amount}
        />
      )}
      <div className="form-group">
        <Button type="submit" bsStyle="primary">
          {buttonLabel}
        </Button>
      </div>
    </div>
  );
};
DonationForm.propTypes = {
  minAmount: PropTypes.number,
  maxAmount: PropTypes.number,
  minAmountError: PropTypes.string,
  maxAmountError: PropTypes.string,
  typeChoices: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string
    })
  ),
  amountChoices: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.objectOf(PropTypes.arrayOf(PropTypes.number))
  ]),
  showTaxCredit: PropTypes.bool,
  byMonth: PropTypes.bool,
  initial: PropTypes.object,
  groupChoices: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      id: PropTypes.string
    })
  ),
  buttonLabel: PropTypes.string,
  hiddenFields: PropTypes.objectOf(PropTypes.string)
};

export default hot(DonationForm);
