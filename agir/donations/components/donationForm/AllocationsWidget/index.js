import React, { useState } from "react";
import PropTypes from "prop-types";

import Button from "@agir/lib/bootstrap/Button";
import {
  changeSingleGroupAllocation,
  changeUnallocatedAmount,
  totalAllocatedFromState
} from "../allocationsReducer";
import { GroupAllocation, GroupSelector } from "./components";
import { AllocationsArray, ButtonHolder, RecipientLabel } from "./Styles";

const filterChoices = currentList => {
  const currentSet = new Set(currentList.map(({ id }) => id));
  return choice => !currentSet.has(choice.id);
};

const AllocationsWidget = ({ groupChoices, value, onChange, maxAmount }) => {
  const [extra, setExtra] = useState(false);

  const currentFilter = filterChoices(value);

  return (
    <>
      <AllocationsArray>
        {(value.length > 0 || extra) && (
          <GroupAllocation
            amount={maxAmount - totalAllocatedFromState(value)}
            maxAmount={maxAmount}
            onChange={amount =>
              onChange(changeUnallocatedAmount(value, maxAmount - amount))
            }
            disabled={value.length === 0}
            step={1}
          >
            <RecipientLabel>Activités nationales</RecipientLabel>
          </GroupAllocation>
        )}
        {value.map(({ id, name, amount }, i) => (
          <GroupAllocation
            key={id}
            amount={amount}
            maxAmount={maxAmount}
            onChange={newAmount =>
              onChange(
                changeSingleGroupAllocation(value, i, newAmount, maxAmount)
              )
            }
            onRemove={() => {
              onChange([...value.slice(0, i), ...value.slice(i + 1)]);
            }}
          >
            <GroupSelector
              value={{ id, name, amount }}
              groupChoices={groupChoices}
              filter={currentFilter}
              onChange={newVal =>
                onChange([
                  ...value.slice(0, i),
                  { amount, ...newVal },
                  ...value.slice(i + 1)
                ])
              }
            />
          </GroupAllocation>
        ))}
        {extra && (
          <GroupAllocation
            onRemove={() => {
              setExtra(false);
            }}
          >
            <GroupSelector
              groupChoices={groupChoices}
              filter={currentFilter}
              onChange={newGroup => {
                setExtra(false);
                onChange(value.concat({ amount: 0, ...newGroup }));
              }}
              value={null}
            />
          </GroupAllocation>
        )}
      </AllocationsArray>
      <ButtonHolder>
        <Button type="button" disabled={extra} onClick={() => setExtra(true)}>
          {value.length === 0 || extra
            ? "Je souhaite allouer mon don à un ou plusieurs groupes"
            : "Allouer à un groupe supplémentaire"}
        </Button>
      </ButtonHolder>
    </>
  );
};

AllocationsWidget.propTypes = {
  groupChoices: PropTypes.arrayOf(
    PropTypes.shape({ id: PropTypes.string, name: PropTypes.string })
  ),
  value: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      amount: PropTypes.number
    })
  ),
  onChange: PropTypes.func,
  maxAmount: PropTypes.number
};

export default AllocationsWidget;
