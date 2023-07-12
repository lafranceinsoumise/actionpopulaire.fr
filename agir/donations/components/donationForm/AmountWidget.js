import React from "react";
import PropTypes from "prop-types";

import AmountInput from "@agir/donations/donationForm/AmountInput";
import { displayPrice } from "@agir/lib/utils/display";
import styled from "styled-components";

import "./style.css";
import { FlexContainer } from "./elements";

const DEFAULT_AMOUNTS = [200 * 100, 100 * 100, 50 * 100, 20 * 100, 10 * 100];

const AmountFlexContainer = styled(FlexContainer)`
  @supports (display: grid) {
    border-radius: 8px;
    padding: 15px;
    display: grid;
    grid-template-columns: 32% 32% 32%;
    grid-template-rows: auto auto;
    grid-gap: 15px;
    align-items: center;
    justify-content: center;
    margin: 0;

    @media (max-width: 992px) {
      grid-template-columns: 48% 48%;
      grid-template-rows: auto auto auto;
    }
  }
`;

const AmountButton = styled.button`
  font-weight: bold;
  border: none;
  height: 55px;
  box-shadow:
    0px 0px 3px rgba(0, 35, 44, 0.3),
    0px 2px 0px rgba(0, 35, 44, 0.15);

  &.btn-unselected {
    background-color: white;
    color: black;
  }
`;

class AmountWidget extends React.Component {
  constructor(props) {
    super();

    const amountChoices = props.amountChoices || DEFAULT_AMOUNTS;

    const custom = props.amount && !amountChoices.includes(props.amount);

    this.state = {
      custom,
    };
  }

  updateWithButton(value) {
    this.setState({ custom: false });
    this.props.onAmountChange(value);
  }

  updateWithCustomValue(value) {
    this.setState({ custom: true });
    this.props.onAmountChange(value);
  }

  render() {
    const { custom } = this.state;
    const { disabled, amount, error, showTaxCredit, paymentTiming } =
      this.props;

    const amountChoices = this.props.amountChoices || DEFAULT_AMOUNTS;

    return (
      <div className="amount-component padtop padbottom">
        <AmountFlexContainer className={error ? " has-error" : ""}>
          {amountChoices.map((value) => (
            <AmountButton
              disabled={disabled}
              key={value}
              type="button"
              onClick={() => this.updateWithButton(value)}
              className={[
                "btn",
                "btn-primary",
                custom || amount !== value ? "btn-unselected" : "",
              ].join(" ")}
            >
              {displayPrice(value)}
            </AmountButton>
          ))}
          <AmountInput
            disabled={disabled}
            placeholder="Autre montant"
            onChange={this.updateWithCustomValue.bind(this)}
            value={custom ? amount : null}
          />

          {error && <span className="help-block">{error}</span>}
        </AmountFlexContainer>
        {showTaxCredit &&
          (amount ? (
            <p className="text-center">
              Si je paye des impôts, après réduction, ma contribution nette sera
              de seulement{" "}
              <strong className="text-danger">
                {displayPrice(amount * 0.34)}
              </strong>
              {paymentTiming && " par mois"}
              &nbsp;!
            </p>
          ) : (
            <p className="text-center">
              Si je paye des impôts, je bénéficie d&apos;une réduction
              d&apos;impôt de <strong>66&nbsp;%</strong> de la somme donnée !
            </p>
          ))}
      </div>
    );
  }
}

AmountWidget.propTypes = {
  disabled: PropTypes.bool,
  amount: PropTypes.number,
  onAmountChange: PropTypes.func,
  error: PropTypes.string,
  amountChoices: PropTypes.arrayOf(PropTypes.number),
  showTaxCredit: PropTypes.bool,
  paymentTiming: PropTypes.bool,
};

export default AmountWidget;
