import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo, useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledInputs = styled.span``;
const StyledInput = styled.input``;
const StyledIcon = styled.span``;
const StyledError = styled.span``;

const StyledField = styled.label`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
  grid-gap: 0 0.75rem;
  align-items: stretch;
  font-size: 0.813rem;
  font-weight: 400;
  line-height: 1;

  & > * {
    margin: 4px 0;
  }

  ${StyledLabel} {
    grid-row: 1;
    grid-column: 1/3;
    font-weight: 600;
  }
  ${StyledHelpText} {
    grid-row: 2;
    grid-column: 1/3;
    line-height: 1.5;
  }
  ${StyledInputs} {
    grid-row: 3;
    grid-column: 1/3;
    max-width: 100%;
    display: flex;
    flex-flow: row nowrap;
  }
  ${StyledInput} {
    flex: 1 1 200px;
    border-radius: 0;
    border: 1px solid;
    border-color: ${({ $invalid }) =>
      $invalid ? style.redNSP : style.black100};
    padding: 0.5rem;
    height: 40px;
    font-size: 1rem;

    &:last-child {
      padding-right: ${({ $invalid }) => ($invalid ? "2.25rem" : "0.5rem")};
    }

    &:focus {
      border-color: ${({ $invalid }) =>
        $invalid ? style.redNSP : style.black1000};
    }

    @media (max-width: ${style.collapse}px) {
      font-size: 0.875rem;
    }
  }

  ${StyledInput} + ${StyledInput} {
    margin-left: 0.5rem;
    flex: 1 1 120px;
  }

  ${StyledIcon} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 3;
    grid-column: 2/3;
    align-items: flex-start;
    justify-content: flex-end;
    padding: 0.5rem;
    color: ${style.redNSP};
  }
  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 4;
    grid-column: 1/3;
    color: ${style.redNSP};
  }
`;

const parseDatetime = (datetime) => {
  const result = {
    date: "",
    time: "",
  };
  try {
    datetime = DateTime.fromISO(datetime, { locale: "fr" });
    result.date = datetime.toFormat("yyyy-MM-dd");
    result.time = datetime.toFormat("HH:mm");
  } catch (e) {
    if (datetime && typeof datetime === "string") {
      result.date = datetime.match(/(\d{4}-\d{2}-\d{1,2}).*/);
      result.date = result.date
        ? result.date[1]
        : new Date().toISOString().substr(0, 10);

      result.time = datetime.match(/(\d{2}:\d{2}).*/);
      result.time = result.time ? result.time[1] : "00:00";
    }
  }
  return result;
};

const stringifyDatetime = (datetime) => {
  let result = datetime.date + "T" + (datetime.time || "00:00") + ":00";
  try {
    result = DateTime.fromISO(result, { locale: "fr" });
    return result.toISO({ includeOffset: false, locale: "fr" });
  } catch (e) {
    return result;
  }
};

const DateTimeField = (props) => {
  const {
    id,
    onChange,
    value,
    type,
    error,
    label,
    helpText,
    autoFocus,
    dateFieldProps,
    timeFieldProps,
    ...rest
  } = props;

  const { time, date } = useMemo(() => parseDatetime(value), [value]);

  const handleChange = useCallback(
    (e) => {
      const datetime = { time, date };
      const now = parseDatetime(new Date().toISOString());
      if (e.target.type === "date") {
        datetime.date = e.target.value || now.date;
      }
      if (e.target.type === "time") {
        datetime.time = e.target.value || now.time;
      }
      onChange && onChange(stringifyDatetime(datetime));
    },
    [onChange, time, date]
  );

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledInputs>
        {type.includes("date") ? (
          <StyledInput
            {...rest}
            {...dateFieldProps}
            type="date"
            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
            onChange={handleChange}
            value={date}
            autoFocus={autoFocus}
          />
        ) : null}
        {type.includes("time") ? (
          <StyledInput
            {...rest}
            {...timeFieldProps}
            type="time"
            pattern="[0-9]{2}:[0-9]{2}"
            step="60"
            onChange={handleChange}
            value={time}
          />
        ) : null}
      </StyledInputs>
      <StyledIcon>
        <FeatherIcon name="alert-circle" />
      </StyledIcon>
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

DateTimeField.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  type: PropTypes.oneOf(["date", "time", "datetime"]),
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
  autoFocus: PropTypes.bool,
  dateFieldProps: PropTypes.object,
  timeFieldProps: PropTypes.object,
};

DateTimeField.defaultProps = {
  type: "datetime",
};

export default DateTimeField;
