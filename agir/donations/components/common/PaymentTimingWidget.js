import PropTypes from "prop-types";
import React, { useEffect } from "react";

import { MONTHLY_PAYMENT, SINGLE_TIME_PAYMENT } from "./form.config";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import {
  Button,
  SelectedButton,
} from "@agir/donations/common/StyledComponents";

const PaymentTimingWidget = (props) => {
  const { value, onChange, disabled, allowedPaymentTimings = [] } = props;

  useEffect(() => {
    allowedPaymentTimings.length < 2 &&
      !allowedPaymentTimings.includes(value) &&
      allowedPaymentTimings[0] &&
      onChange(allowedPaymentTimings[0]);
  }, [value, onChange, allowedPaymentTimings]);

  if (allowedPaymentTimings.length < 2) {
    return null;
  }

  return (
    <div style={{ display: "flex", marginTop: "2rem" }}>
      <Button
        type="button"
        icon={value === MONTHLY_PAYMENT ? "check" : undefined}
        as={value === MONTHLY_PAYMENT ? SelectedButton : Button}
        disabled={disabled}
        onClick={() => onChange(MONTHLY_PAYMENT)}
        style={{
          flex: "1 1 auto",
          borderTopRightRadius: 0,
          borderBottomRightRadius: 0,
        }}
      >
        Tous les mois
      </Button>
      <Button
        type="button"
        icon={value === SINGLE_TIME_PAYMENT ? "check" : undefined}
        as={value === SINGLE_TIME_PAYMENT ? SelectedButton : Button}
        disabled={disabled}
        onClick={() => onChange(SINGLE_TIME_PAYMENT)}
        style={{
          flex: "1 1 auto",
          borderTopLeftRadius: 0,
          borderBottomLeftRadius: 0,
        }}
      >
        Une seule fois
      </Button>
    </div>
  );
};

PaymentTimingWidget.propTypes = {
  value: PropTypes.oneOf([MONTHLY_PAYMENT, SINGLE_TIME_PAYMENT]),
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  allowedPaymentTimings: PropTypes.arrayOf(
    PropTypes.oneOf([MONTHLY_PAYMENT, SINGLE_TIME_PAYMENT]),
  ),
};

export default PaymentTimingWidget;
