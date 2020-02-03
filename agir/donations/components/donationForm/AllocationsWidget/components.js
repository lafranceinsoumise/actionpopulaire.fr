import InputRange from "@agir/lib/bootstrap/InputRange";
import AmountInput from "@agir/donations/donationForm/AmountInput";
import PropTypes from "prop-types";
import React from "react";
import Async from "react-select/async";

import {
  AlignedButton,
  AmountBoxContainer,
  RecipientContainer,
  Row,
  SliderContainer
} from "@agir/donations/donationForm/AllocationsWidget/Styles";
import search from "@agir/donations/donationForm/AllocationsWidget/search";
import { debounce } from "@agir/lib/utils/promises";

const debouncedSearch = debounce(search, 200);

export const RemoveButton = ({ onClick }) => (
  <AlignedButton
    type="button"
    className="fa"
    onClick={onClick || (() => null)}
    title={"Ne plus flécher vers ce groupe"}
  >
    {onClick ? "\uf00d" : ""}
  </AlignedButton>
);
RemoveButton.propTypes = {
  onClick: PropTypes.func
};

export const GroupAllocation = ({
  amount,
  maxAmount,
  onChange,
  onRemove,
  disabled,
  children
}) => (
  <Row>
    <RecipientContainer>{children}</RecipientContainer>
    <SliderContainer>
      <InputRange
        maxValue={maxAmount}
        minValue={0}
        value={amount}
        onChange={onChange}
        disabled={disabled}
        step={1}
      />
    </SliderContainer>
    <AmountBoxContainer>
      <AmountInput
        value={amount}
        onChange={v => {
          if (v === null) {
            onChange(0);
          }
          if (v >= 0 && v <= maxAmount) {
            onChange(v);
          }
        }}
      />
    </AmountBoxContainer>
    <RemoveButton onClick={onRemove} />
  </Row>
);
GroupAllocation.propTypes = {
  children: PropTypes.node,
  amount: PropTypes.number,
  maxAmount: PropTypes.number,
  onChange: PropTypes.func,
  onRemove: PropTypes.func,
  disabled: PropTypes.bool
};
GroupAllocation.defaultProps = {
  amount: 0,
  maxAmount: 0,
  onChange: () => null,
  onRemove: null,
  disabled: false
};

export const GroupSelector = ({ groupChoices, onChange, value, filter }) => {
  const defaultOptions = {
    label: "Mes groupes",
    options: groupChoices.filter(filter)
  };
  return (
    <Async
      value={value}
      loadOptions={terms =>
        debouncedSearch(terms).then(options =>
          options.length
            ? [
                {
                  label: "Ma recherche",
                  options: options
                },
                defaultOptions
              ]
            : []
        )
      }
      defaultOptions={[defaultOptions]}
      filterOption={({ data }) => filter(data)}
      getOptionLabel={({ name }) => name}
      getOptionValue={({ id }) => id}
      formatGroupLabel={g => {
        console.log(g);
        return g.label;
      }}
      onChange={onChange}
      loadingMessage={() => "Recherche..."}
      noOptionsMessage={({ inputValue }) =>
        inputValue.length < 3
          ? "Entrez au moins 3 lettres pour chercher un groupe"
          : "Pas de résultats"
      }
      placeholder="Cherchez un groupe..."
    >
      {groupChoices.map(({ name, id }) => (
        <option key={id} value={id}>
          {name}
        </option>
      ))}
    </Async>
  );
};
GroupSelector.propTypes = {
  onChange: PropTypes.func,
  groupChoices: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string
    })
  ),
  value: PropTypes.shape({ id: PropTypes.string, name: PropTypes.string }),
  filter: PropTypes.func
};
GroupSelector.defaultProps = {
  onChange: () => null,
  filter: () => true,
  groupChoices: [],
  value: null
};
