import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Spacer from "@agir/front/genericComponents/Spacer";
import { Hide } from "@agir/front/genericComponents/grid";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledCustomField = styled.div`
  @media (min-width: ${style.collapse}px) {
    display: grid;
    grid-template-columns: 10rem 30.25rem;
    gap: 0.25rem;
    align-items: center;
  }
`;

const StyledDescription = styled.div`
  margin-left: 10.5rem;
  font-size: 0.8125rem;

  @media (max-width: ${style.collapse}px) {
    margin-bottom: 0.25rem;
    margin-left: 0;
    font-size: 0.875rem;
  }
`;

const CustomField = ({
  Component,
  noSpacer = false,
  id,
  label,
  helpText,
  className,
  ...rest
}) => {
  const isDesktop = useIsDesktop();

  return (
    <div className={className}>
      <StyledCustomField htmlFor={id}>
        <Hide $under as="label">
          {label}
        </Hide>
        <Component
          {...rest}
          label={(!isDesktop && label) || ""}
          helpText={(!isDesktop && helpText) || ""}
        />
      </StyledCustomField>
      {!!helpText && (
        <Hide $under as={StyledDescription}>
          {helpText}
        </Hide>
      )}
      {!noSpacer && <Spacer size="1rem" />}
    </div>
  );
};

CustomField.propTypes = {
  Component: PropTypes.elementType.isRequired,
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  label: PropTypes.string,
  helpText: PropTypes.string,
  noSpacer: PropTypes.bool,
  className: PropTypes.string,
};

export default CustomField;
