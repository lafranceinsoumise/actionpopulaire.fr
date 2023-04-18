import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import RangeField from "@agir/front/formComponents/RangeField";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

const StyledRangeField = styled(RangeField)``;
const StyledField = styled.div`
  margin: 1.5rem 0;
  position: relative;
`;

const ActionRadiusField = (props) => {
  const { value = null, onChange, disabled, min, max } = props;

  return (
    <PageFadeIn ready={value !== null}>
      <StyledField>
        <StyledRangeField
          value={value}
          onChange={onChange}
          disabled={disabled}
          label="Proposer des événements dans un rayon de :"
          helpText={
            <p style={{ margin: "0.25rem 0 0", textAlign: "right" }}>
              Un doute sur la localisation utilisée&nbsp;?&ensp;
              <Link route="personalInformation">Vérifiez ici</Link>
            </p>
          }
          min={min}
          max={max}
        />
      </StyledField>
    </PageFadeIn>
  );
};

ActionRadiusField.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  min: PropTypes.number,
  max: PropTypes.number,
};

export default ActionRadiusField;
