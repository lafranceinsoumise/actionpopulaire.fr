import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo } from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import { WarningBlock } from "@agir/elections/Common/StyledComponents";

const StyledLabel = styled.p``;
const StyledHelpText = styled.p``;
const StyledField = styled.p``;
const StyledError = styled.p``;
const StyledFieldset = styled.fieldset`
  display: flex;
  flex-flow: column nowrap;
  gap: 4px;
  margin: 0;

  && > * {
    margin: 0;
    padding: 0;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
  }

  ${StyledLabel} {
    display: block;
    font-weight: 600;
  }

  ${StyledError} {
    color: ${style.redNSP};
  }
`;

const VotingDateFields = (props) => {
  const {
    name,
    value,
    onChange,
    options,
    error,
    label,
    labelSingle,
    helpText,
  } = props;

  const handleChange = useCallback(
    ({ target }) => {
      onChange(
        target.checked
          ? [...value, target.value]
          : value.filter((item) => item !== target.value),
      );
    },
    [onChange, value],
  );

  const activeOptions = useMemo(
    () =>
      options.filter((option) => {
        const oneDay = 1 * 24 * 60 * 60 * 1000; // Remove options the day before the date
        return (
          new Date(option.value).setHours(0, 0, 0, 0).valueOf() - oneDay >
          new Date(new Date().setHours(0, 0, 0, 0).valueOf())
        );
      }),
    [options],
  );

  const displayLabel = useMemo(() => {
    if (labelSingle && activeOptions.length === 1) {
      return labelSingle;
    }

    return label;
  }, [label, labelSingle, activeOptions]);

  useEffect(() => {
    activeOptions.length === 1 &&
      !value.includes(activeOptions[0].value) &&
      onChange([activeOptions[0].value]);
  }, [value, activeOptions, onChange]);

  if (activeOptions.length === 0) {
    return (
      <WarningBlock icon="x-circle" background="#ffe8d7" iconColor="#ff8c37">
        Il n'est désormais plus possible de faire de demandes, car la date de
        l'élection est trop proche ou est passée.
      </WarningBlock>
    );
  }

  return (
    <StyledFieldset>
      {label && <StyledLabel>{displayLabel}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledField>
        {activeOptions.map((option) => (
          <CheckboxField
            toggle={activeOptions.length === 1}
            key={option.value}
            name={name}
            label={option.label}
            value={value.includes(option.value)}
            onChange={handleChange}
            inputValue={option.value}
          />
        ))}
      </StyledField>

      {error && <StyledError>{error}</StyledError>}
    </StyledFieldset>
  );
};

VotingDateFields.propTypes = {
  name: PropTypes.string.isRequired,
  value: PropTypes.arrayOf(PropTypes.string).isRequired,
  onChange: PropTypes.func,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string,
    }),
  ).isRequired,
  id: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  label: PropTypes.node,
  labelSingle: PropTypes.node,
  helpText: PropTypes.node,
};

export default VotingDateFields;
