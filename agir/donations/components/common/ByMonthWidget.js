import PropTypes from "prop-types";
import React from "react";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import {
  Button,
  SelectedButton,
} from "@agir/donations/common/StyledComponents";

const ByMonthWidget = (props) => {
  const { value, onChange, disabled } = props;

  return (
    <div style={{ display: "flex", marginTop: "2rem" }}>
      <Button
        type="button"
        as={value === true ? SelectedButton : Button}
        disabled={disabled}
        onClick={() => onChange(true)}
        style={{
          flex: "1 1 auto",
          borderTopRightRadius: 0,
          borderBottomRightRadius: 0,
        }}
      >
        {value === true ? <RawFeatherIcon name="check" /> : null}
        Tous les mois
      </Button>
      <Button
        type="button"
        as={value === false ? SelectedButton : Button}
        disabled={disabled}
        onClick={() => onChange(false)}
        style={{
          flex: "1 1 auto",
          borderTopLeftRadius: 0,
          borderBottomLeftRadius: 0,
        }}
      >
        {value === false ? <RawFeatherIcon name="check" /> : null}
        Une seule fois
      </Button>
    </div>
  );
};

ByMonthWidget.propTypes = {
  value: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

export default ByMonthWidget;
