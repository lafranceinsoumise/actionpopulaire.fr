import React, { useState } from "react";
import PropTypes from "prop-types";

import Button from "@agir/lib/bootstrap/Button";
import {
  changeSingleGroupAllocation,
  changeUnallocatedAmount,
  totalAllocatedFromState
} from "../allocationsReducer";
import { GroupAllocation, GroupPicker } from "./components";
import { AllocationsArray, ButtonHolder } from "./Styles";

const AllocationsWidget = ({ groupChoices, value, onChange, maxAmount }) => {
  const [extra, setExtra] = useState(false);

  const extraGroups = groupChoices.filter(choice =>
    value.every(allocation => allocation.group !== choice.id)
  );

  return (
    <>
      <AllocationsArray>
        {(value.length > 0 || extra) && (
          <GroupAllocation
            label="Activités nationales"
            amount={maxAmount - totalAllocatedFromState(value)}
            maxAmount={maxAmount}
            onChange={amount =>
              onChange(changeUnallocatedAmount(value, maxAmount - amount))
            }
            disabled={value.length === 0}
            step={1}
          />
        )}
        {value.map(({ group, amount }, i) => (
          <GroupAllocation
            key={group}
            label={groupChoices.find(choice => choice.id === group).name}
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
          />
        ))}
        {extra && (
          <GroupPicker
            groupChoices={extraGroups}
            onChange={id => {
              setExtra(false);
              onChange(value.concat({ group: id, amount: 0 }));
            }}
          />
        )}
      </AllocationsArray>
      <ButtonHolder>
        <Button
          type="button"
          disabled={extra || extraGroups.length === 0}
          onClick={() =>
            extraGroups.length > 1
              ? setExtra(true)
              : onChange(
                  value.concat([{ group: extraGroups[0].id, amount: 0 }])
                )
          }
        >
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
    PropTypes.shape({ group: PropTypes.string, amount: PropTypes.number })
  ),
  onChange: PropTypes.func,
  maxAmount: PropTypes.number
};

export default AllocationsWidget;
