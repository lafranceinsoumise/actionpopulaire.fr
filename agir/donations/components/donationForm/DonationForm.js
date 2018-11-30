import React from 'react';
import {hot} from 'react-hot-loader';

import AllocationSlider from './AllocationSlider';
import AmountWidget from './AmountWidget';
import GroupSelector from './GroupSelector';
import PropTypes from 'prop-types';

import Button from 'lib/bootstrap/Button';
import {displayPrice} from 'lib/utils';

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
    return (this.state.amount);
  }

  groupName() {
    if (!this.state.group) return null;
    return this.props.groupName || this.props.groupChoices.find(g => g.value === this.state.group).label;
  }

  render() {
    const {groupChoices, csrfToken, minAmount, maxAmount} = this.props;
    const {group, amount, nationalRatio} = this.state;

    const customError = amount === null
      ? null
      : amount < minAmount
        ? `Il n'est pas possible de donner moins de ${displayPrice(minAmount)} par carte bleue.`
        : amount > maxAmount
          ? `Il n'est pas possible de donner plus de ${displayPrice(maxAmount)} par carte bleue.`
          : null;

    return <div>
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken}/>
      <AmountWidget amount={amount} error={customError} onAmountChange={(amount => this.setState({amount}))}/>
      {groupChoices &&
      <GroupSelector choices={groupChoices} value={group} onGroupChange={(group) => this.setState({group})}/>
      }
      {(group || groupChoices) &&
      <AllocationSlider
        disabled={!group} donation={amount} nationalRatio={nationalRatio} groupName={this.groupName()}
        onAllocationChange={nationalRatio => this.setState({nationalRatio})}
      />
      }
      <div className="form-group">
        <Button type="submit" bsStyle="primary">Je donne !</Button>
      </div>
    </div>;
  }

}

DonationForm.propTypes = {
  minAmount: PropTypes.number,
  maxAmount: PropTypes.number,
  initialGroup: PropTypes.string,
  groupName: PropTypes.string,
  groupChoices: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.string,
    label: PropTypes.string
  })),
  csrfToken: PropTypes.string
};


export default hot(module)(DonationForm);
