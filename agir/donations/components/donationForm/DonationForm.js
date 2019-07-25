import React from "react";
import { hot } from "react-hot-loader";

import AllocationSlider from "./AllocationSlider";
import AmountWidget from "./AmountWidget";
import GroupSelector from "./GroupSelector";
import PropTypes from "prop-types";

import Button from "@agir/lib/bootstrap/Button";

class DonationForm extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      group: props.initialGroup,
      amount: null,
      nationalRatio: 50
    };
  }

  isValid() {
    return this.state.amount;
  }

  groupName() {
    if (!this.state.group) return null;
    return (
      this.props.groupName ||
      this.props.groupChoices.find(g => g.value === this.state.group).label
    );
  }

  render() {
    const {
      groupChoices,
      csrfToken,
      minAmount,
      maxAmount,
      minAmountError,
      maxAmountError,
      amountChoices,
      showTaxCredit,
      buttonLabel,
      byMonth
    } = this.props;
    const { group, amount, nationalRatio } = this.state;

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
        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
        <AmountWidget
          amount={amount}
          amountChoices={amountChoices}
          showTaxCredit={showTaxCredit}
          byMonth={byMonth}
          error={customError}
          onAmountChange={amount => this.setState({ amount })}
        />
        {groupChoices && (
          <GroupSelector
            choices={groupChoices}
            value={group}
            onGroupChange={group => this.setState({ group })}
            showOtherGroupHelp={!byMonth}
          />
        )}
        {(group || groupChoices) && (
          <AllocationSlider
            disabled={!group}
            donation={amount}
            nationalRatio={nationalRatio}
            groupName={this.groupName()}
            onAllocationChange={nationalRatio =>
              this.setState({ nationalRatio })
            }
          />
        )}
        <div className="form-group">
          <Button type="submit" bsStyle="primary">
            {buttonLabel}
          </Button>
        </div>
      </div>
    );
  }
}

DonationForm.propTypes = {
  minAmount: PropTypes.number,
  maxAmount: PropTypes.number,
  minAmountError: PropTypes.string,
  maxAmountError: PropTypes.string,
  amountChoices: PropTypes.array,
  showTaxCredit: PropTypes.bool,
  byMonth: PropTypes.bool,
  initialGroup: PropTypes.string,
  groupName: PropTypes.string,
  groupChoices: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string
    })
  ),
  buttonLabel: PropTypes.string,
  csrfToken: PropTypes.string
};

export default hot(module)(DonationForm);
