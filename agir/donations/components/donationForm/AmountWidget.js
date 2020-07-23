import React from "react";
import PropTypes from "prop-types";

import AmountInput from "@agir/donations/donationForm/AmountInput";
import { displayPrice } from "@agir/lib/utils/display";
import styled from "styled-components";

import "./style.css";
import { FlexContainer } from "./elements";

const DEFAULT_AMOUNTS = [200 * 100, 100 * 100, 50 * 100, 20 * 100, 10 * 100];

const AmountButton = styled.button`
  display: block;
  width: 30%;
  height: 50px;
  margin: 10px 0;
  font-weight: bold;
  min-width: 200px;
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
    const { disabled, amount, error, showTaxCredit, byMonth } = this.props;

    const amountChoices = this.props.amountChoices || DEFAULT_AMOUNTS;

    return (
      <div className="amount-component">
        <FlexContainer className={error ? " has-error" : ""}>
          {amountChoices.map((value) => (
            <AmountButton
              disabled={disabled}
              key={value}
              type="button"
              onClick={() => this.updateWithButton(value)}
              className={[
                "btn",
                custom || amount !== value ? "btn-default" : "btn-primary",
              ].join(" ")}
            >
              {displayPrice(value)}
            </AmountButton>
          ))}
          <AmountInput
            disabled={disabled}
            placeholder="autre montant"
            onChange={this.updateWithCustomValue.bind(this)}
            value={custom ? amount : null}
          />

          {error && <span className="help-block">{error}</span>}
        </FlexContainer>
        <p>
          {showTaxCredit &&
            (amount ? (
              <em>
                Si je paye des impôts, après réduction, ma contribution nette
                sera de seulement{" "}
                <strong className="text-danger">
                  {displayPrice(amount * 0.34)}
                </strong>
                {byMonth && " par mois"}
                &nbsp;!
              </em>
            ) : (
              <em>
                Si je paye des impôts, je bénéficie d&apos;une réduction
                d&apos;impôt de <strong>66&nbsp;%</strong> de la somme donnée !
              </em>
            ))}
        </p>
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
  byMonth: PropTypes.bool,
};

export default AmountWidget;
