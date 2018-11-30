import React from 'react';
import InputRange from 'react-input-range';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import './AllocationSlider.css';

import {displayPrice} from 'lib/utils';

const Container = styled.div`
  max-height: ${props => props.open ? '600px' : '0'};
  transition: max-height 0.6s ease-out;
  overflow: hidden;
`;

const Flex = styled.div`
  display: flex;
  flex-wrap: wrap;
  margin: auto -4px auto 0;
  `;

const ValueBlock = styled.div`
  box-sizing: border-box;
  width: 50%;
  padding: 5%;
  text-align: center;
  border-right: 4px dotted #aaa;  
`;

const Amount = styled.span`
  width: auto;
  font-size: 2em;
  border-bottom: 2px dotted #555;
  margin: 5px auto;
`;

const AllocationSlider = ({donation, nationalRatio, onAllocationChange, disabled, groupName}) => {
  const nationalAmount = donation ? Math.round(donation * nationalRatio) / 100 : '';
  const allocation = donation ? donation - nationalAmount : '';
  const shownRatio = Math.round(nationalRatio);

  return <Container className="form-group" open={!disabled}>
    <input type="hidden" name="allocation" value={allocation}/>
    <div style={{overflow: 'hidden'}}>
      <label htmlFor="allocation-slider">Comment souhaitez-vous répartir votre don ?</label>
      <Flex>
        <ValueBlock>
          <div>
            <Amount>{nationalAmount === '' ? '--,-- €' : displayPrice(nationalAmount)}</Amount>
          </div>
          Activités et campagnes nationales de la France insoumise
        </ValueBlock>
        <ValueBlock right>
          <div>
            <Amount>{allocation === '' ? '--,-- €' : displayPrice(allocation)}</Amount>
          </div>
          Activités du groupe
          <div>
            {groupName && <React.Fragment>&laquo;&nbsp;<strong>{groupName}</strong>&nbsp;&raquo;</React.Fragment>}
          </div>

        </ValueBlock>
      </Flex>
      <InputRange
        maxValue={100}
        minValue={0}
        value={shownRatio}
        onChange={v => onAllocationChange(v)}
        disabled={disabled}
      />
    </div>
  </Container>;
};
AllocationSlider.propTypes = {
  donation: PropTypes.number,
  allocationRatio: PropTypes.number,
  onAllocationChange: PropTypes.func,
  disabled: PropTypes.bool,
  groupName: PropTypes.string
};

export default AllocationSlider;
