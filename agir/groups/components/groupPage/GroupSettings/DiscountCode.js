import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import ShareLink from "@agir/front/genericComponents/ShareLink";

const StyledDiscountCode = styled.div`
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: ${(props) => (props.$special ? "none" : props.theme.cardShadow)};
  background-color: ${(props) =>
    props.$special ? props.theme.primary100 : "transparent"};

  & > * {
    margin: 0;
    padding: 0;
  }

  & > h5 {
    font-weight: 700;
    font-size: 16px;
    line-height: 1.5;
    padding-bottom: 0.5rem;

    span {
      text-transform: capitalize;
    }
  }

  & > div {
    max-width: 360px;
  }

  & > p {
    padding-top: 0.75rem;
    color: ${(props) => props.theme.black700};
    font-size: 0.875rem;
    line-height: 1.5;
  }
`;

const DiscountCode = ({ code, dateExact, month, label }) => (
  <StyledDiscountCode $special={!!label}>
    {label ? (
      <h5>🎟️&nbsp;{label}</h5>
    ) : (
      <h5>Code promo matériel du mois de {month}</h5>
    )}
    <ShareLink color="secondary" url={code} label="Copier" $wrap={400} />
    <p>Valable jusqu'au {dateExact}</p>
  </StyledDiscountCode>
);

DiscountCode.propTypes = {
  code: PropTypes.string.isRequired,
  dateExact: PropTypes.string.isRequired,
  month: PropTypes.string,
  label: PropTypes.string,
};
export default DiscountCode;
