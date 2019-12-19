import InputRange from "@agir/lib/bootstrap/InputRange";
import AmountInput from "@agir/donations/donationForm/AmountInput";
import PropTypes from "prop-types";
import React from "react";
import {
  AmountBoxContainer,
  RecipientLabel,
  Row,
  AlignedButton,
  SliderContainer,
  AlignedSelect
} from "@agir/donations/donationForm/AllocationsWidget/Styles";

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

export const GroupPicker = ({ onChange, onRemove, groupChoices }) => (
  <Row>
    <AlignedSelect value="" onChange={e => onChange(e.target.value)}>
      <option value="">Sélectionnez un groupe</option>
      {groupChoices.map(({ name, id }) => (
        <option key={id} value={id}>
          {name}
        </option>
      ))}
    </AlignedSelect>
    <SliderContainer>
      <InputRange disabled={true} />
    </SliderContainer>
    <AmountBoxContainer>
      <AmountInput disabled={true} />
    </AmountBoxContainer>
    <RemoveButton onClick={onRemove} />
  </Row>
);
GroupPicker.propTypes = {
  onChange: PropTypes.func,
  onRemove: PropTypes.func,
  groupChoices: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string
    })
  )
};
GroupPicker.defaultProps = {
  onChange: () => null,
  onRemove: () => null,
  groupChoices: []
};

export const GroupAllocation = ({
  label,
  amount,
  maxAmount,
  onChange,
  onRemove,
  disabled
}) => (
  <Row>
    <RecipientLabel>{label}</RecipientLabel>

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
  label: PropTypes.string,
  amount: PropTypes.number,
  maxAmount: PropTypes.number,
  onChange: PropTypes.func,
  onRemove: PropTypes.func,
  disabled: PropTypes.bool
};
GroupAllocation.defaultProps = {
  label: "",
  amount: 0,
  maxAmount: 0,
  onChange: () => null,
  onRemove: null,
  disabled: false
};
