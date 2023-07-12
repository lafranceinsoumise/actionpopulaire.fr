import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { displayPrice } from "@agir/lib/utils/display";
import { TYPE_LABEL, TYPE_GROUP } from "./allocations.config";

const StyledAllocationDetails = styled.div`
  padding: 1rem;
  background-color: ${(props) => props.theme.primary100};
  border-radius: 4px;

  strong {
    font-weight: 600;
  }

  ul {
    margin: 0;
    padding: 0;
    list-style: none;
    font-size: 0.875rem;

    li {
      &::before {
        content: "― ";
      }
    }
  }
`;

const AllocationDetails = (props) => {
  const { groupName, totalAmount, allocations, byMonth = false } = props;
  if (!Array.isArray(allocations) || allocations.length === 0) {
    return null;
  }
  const unit = byMonth ? "€/mois" : "€";
  return (
    <StyledAllocationDetails>
      Je fais un don de{" "}
      <strong>{displayPrice(totalAmount, false, unit)}</strong> qui sera ainsi
      réparti :
      <br />
      <ul>
        {allocations.map(
          (allocation) =>
            !!allocation.value && (
              <li key={allocation.type}>
                <strong>{displayPrice(allocation.value, false, unit)}</strong>{" "}
                {TYPE_LABEL[allocation.type]}
                {allocation.type === TYPE_GROUP && groupName ? (
                  <em> {groupName}</em>
                ) : null}
              </li>
            ),
        )}
      </ul>
    </StyledAllocationDetails>
  );
};

AllocationDetails.propTypes = {
  groupName: PropTypes.string,
  totalAmount: PropTypes.number,
  allocations: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    }),
  ),
  byMonth: PropTypes.bool,
};

export default AllocationDetails;
