import React, { useState } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import Button from "@agir/lib/bootstrap/Button";

import { changeTotalAmount } from "./allocationsReducer";
import AllocationWidget from "./AllocationsWidget";
import AmountWidget from "./AmountWidget";
import TypeWidget from "./TypeWidget";

const Title = styled.h4`
  counter-increment: sectionformulaire;

  &:before {
    display: block;
    font-size: 1.4em;
    line-height: 1.5;
    content: counter(sectionformulaire) ".";
  }
`;

const addLabelToAllocations = (allocations, groupChoices) => {
  if (!allocations) {
    return [];
  }

  return allocations.map(({ group, amount }) => ({
    id: group,
    name: groupChoices.find(({ id }) => id === group).name,
    amount,
  }));
};

const serializeAllocations = (allocations) => {
  if (!allocations) {
    return [];
  }

  return JSON.stringify(
    allocations
      .filter(({ amount }) => amount != 0)
      .map(({ id, amount }) => ({ group: id, amount }))
  );
};

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
  enableAllocations,
  typeActe,
}) => {
  const [type, setType] = useState(initial.type || null);
  const [allocations, setAllocations] = useState(
    addLabelToAllocations(initial.allocations, groupChoices)
  );
  const [amount, setAmount] = useState(initial.amount || null);

  const customError =
    amount === null
      ? null
      : minAmount && amount < minAmount
      ? minAmountError
      : maxAmount && amount > maxAmount
      ? maxAmountError
      : null;

  const valid =
    (!typeChoices || type !== null) && amount !== null && amount > 0;

  return (
    <form
      method="post"
      onSubmit={(e) => valid || e.preventDefault()}
      className="text-center"
    >
      {Object.keys(hiddenFields).map((k) => (
        <input key={k} type="hidden" name={k} value={hiddenFields[k]} />
      ))}
      <input type="hidden" name="type" value={type || ""} />
      <input type="hidden" name="amount" value={amount || ""} />
      <input
        type="hidden"
        name="allocations"
        value={serializeAllocations(allocations)}
      />
      {enableAllocations || typeChoices ? (
        <Title>Je choisis le montant de {typeActe}</Title>
      ) : (
        <h4>Je choisis le montant de {typeActe}</h4>
      )}
      <AmountWidget
        amount={amount}
        amountChoices={amountChoices}
        showTaxCredit={showTaxCredit}
        byMonth={type === "M"}
        error={customError}
        onAmountChange={(newAmount) => {
          setAmount(newAmount);
          setAllocations(changeTotalAmount(allocations, amount, newAmount));
        }}
      />
      {typeChoices && (
        <>
          <Title>Je choisis de donner une fois ou chaque mois</Title>
          {type === "M" && (
            <p className="help-block">
              <i className="fa fa-warning"></i>&ensp;Seul le don par carte bleue
              est possible pour un don mensuel.
            </p>
          )}
          <TypeWidget
            type={type}
            typeChoices={typeChoices}
            onTypeChange={(type) => {
              setType(type);
            }}
          />
        </>
      )}

      {enableAllocations && (
        <>
          <Title>Je choisis une répartition pour {typeActe}</Title>
          <AllocationWidget
            groupChoices={groupChoices}
            value={allocations}
            onChange={setAllocations}
            maxAmount={amount}
          />
        </>
      )}

      <div className="form-group">
        <div style={{ maxWidth: 500, margin: "20px auto" }}>
          <Button type="submit" className="btn btn-primary btn-block btn-lg">
            Je donne !
          </Button>
        </div>
      </div>
    </form>
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
      label: PropTypes.string,
    })
  ),
  amountChoices: PropTypes.arrayOf(PropTypes.number),
  showTaxCredit: PropTypes.bool,
  byMonth: PropTypes.bool,
  initial: PropTypes.object,
  groupChoices: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      id: PropTypes.string,
    })
  ),
  hiddenFields: PropTypes.objectOf(PropTypes.string),
  typeActe: PropTypes.string,
  enableAllocations: PropTypes.bool,
};

DonationForm.defaultProps = {
  minAmount: 0,
  maxAMount: 100000,
  groupChoices: [],
  typeActe: "mon don",
  enableAllocations: true,
};

export default DonationForm;
