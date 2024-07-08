import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { displayPrice } from "@agir/lib/utils/display";
import { TYPE_LABEL, TYPE_GROUP } from "./allocations.config";
import StaticToast from "@agir/front/genericComponents/StaticToast";

const StyledStaticToast = styled(StaticToast)`
  p {
    strong {
      font-weight: 600;
    }

    q {
      &::before {
        content: "« ";
      }
      &::after {
        content: " »";
      }
    }
  }
`;

const StyledAllocationDetails = styled.div`
  padding: 1rem;
  color: ${(props) => props.theme.textColor};
  background-color: ${(props) => props.theme.primary100};
  border-radius: 4px;

  strong {
    font-weight: 600;
  }

  ul {
    padding-left: 1rem;
    margin: 0.5rem 0 0;
    font-size: 0.875rem;

    &:first-child {
      font-size: 1rem;
      margin: 0;
    }

    strong {
      font-feature-settings: "tnum";
      font-variant-numeric: tabular-nums;
    }

    q {
      font-weight: 500;

      &::before {
        content: "« ";
      }
      &::after {
        content: " »";
      }
    }
  }
`;

export const InactiveGroupAllocation = ({ allocation, byMonth }) => {
  if (!allocation || !allocation.group) {
    return null;
  }

  const unit = byMonth ? "€∕mois" : "€";

  return (
    <StyledStaticToast>
      <p>
        Le groupe{" "}
        <strong>
          <q>{allocation.group.name}</q>
        </strong>{" "}
        a qui vous aviez attribué{" "}
        <strong>{displayPrice(allocation.value, false, unit)}</strong> n'est
        plus {!allocation.group.isCertified ? "certifié" : "actif"} et ne peut
        donc plus recevoir de dons.
      </p>
    </StyledStaticToast>
  );
};

InactiveGroupAllocation.propTypes = {
  allocation: PropTypes.shape({
    group: PropTypes.shape({
      name: PropTypes.string,
      isCertified: PropTypes.bool,
    }),
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  }),
  byMonth: PropTypes.bool,
};

const AllocationDetails = (props) => {
  const { groupName, totalAmount, allocations, byMonth = false } = props;

  if (!Array.isArray(allocations) || allocations.length === 0) {
    return null;
  }

  const unit = byMonth ? "€∕mois" : "€";

  return (
    <StyledAllocationDetails>
      {typeof totalAmount === "number" && (
        <>
          Je fais un don de{" "}
          <strong>{displayPrice(totalAmount, false, unit)}</strong> qui sera
          ainsi réparti :
          <br />
        </>
      )}
      <ul>
        {allocations.map(
          (allocation) =>
            !!allocation.value && (
              <li key={allocation.type}>
                <strong>{displayPrice(allocation.value, true, unit)}</strong>{" "}
                {TYPE_LABEL[allocation.type]}
                {allocation.type === TYPE_GROUP && groupName ? (
                  <>
                    {" "}
                    <q>{groupName}</q>
                  </>
                ) : null}
                {allocation?.departement?.name ? (
                  <span> ({allocation.departement.name})</span>
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
