import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Spacer from "@agir/front/genericComponents/Spacer";
import { Hide } from "@agir/front/genericComponents/grid";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledCustomField = styled.div`
  @media (min-width: ${style.collapse}px) {
    display: flex;
    align-items: center;
    > label:first-of-type {
      margin-top: 4px;
      width: 160px;
      margin: 0;
      margin-right: 4px;
    }
    > label:nth-of-type(2) {
      flex-grow: 1;
    }
  }
`;

const StyledDescription = styled.div`
  margin-left: 168px;
  font-size: 13px;
  @media (max-width: ${style.collapse}px) {
    margin-bottom: 4px;
    margin-left: 0;
    font-size: 14px;
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
        <Hide under as="label">
          {label}
        </Hide>
        <Component
          {...rest}
          label={(!isDesktop && label) || ""}
          helpText={(!isDesktop && helpText) || ""}
        />
      </StyledCustomField>
      {!!helpText && (
        <Hide under as={StyledDescription}>
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
