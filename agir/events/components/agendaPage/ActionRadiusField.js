import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import RangeField from "@agir/front/formComponents/RangeField";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

const StyledLink = styled(Link)``;
const StyledRangeField = styled(RangeField)``;
const StyledField = styled.div`
  margin: 1.5rem 0;
  position: relative;

  ${StyledLink} {
    position: absolute;
    top: 0;
    right: 0;
    font-size: 0.875rem;
    font-weight: 600;
  }
`;

const ActionRadiusField = (props) => {
  const { value, onChange, disabled } = props;

  return (
    <PageFadeIn ready={!!value}>
      <StyledField>
        <StyledRangeField
          value={value}
          onChange={onChange}
          disabled={disabled}
          label="Proposer des événements dans un rayon de :"
          min={1}
          max={500}
          step={1}
        />
        <StyledLink route="personalInformation">
          Changer ma localisation{" "}
          <FeatherIcon name="external-link" small inline />
        </StyledLink>
      </StyledField>
    </PageFadeIn>
  );
};

ActionRadiusField.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
};

export default ActionRadiusField;
