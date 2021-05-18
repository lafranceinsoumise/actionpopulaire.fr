import InputRange from "@agir/front/genericComponents/InputRange";
import AmountInput from "@agir/donations/donationForm/AmountInput";
import PropTypes from "prop-types";
import React from "react";

import {
  AlignedButton,
  AmountBoxContainer,
  RecipientContainer,
  Row,
  SliderContainer,
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
  onClick: PropTypes.func,
};

export const GroupAllocation = ({
  amount,
  maxAmount,
  onChange,
  onRemove,
  disabled,
  children,
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
        disabled={disabled}
        onChange={(v) => {
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
  disabled: PropTypes.bool,
};
GroupAllocation.defaultProps = {
  amount: 0,
  maxAmount: 0,
  onChange: () => null,
  onRemove: null,
  disabled: false,
};
