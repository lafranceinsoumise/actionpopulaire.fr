import moment from "moment";
import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import Datetime from "react-datetime";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

import "moment/locale/fr";
import "react-datetime/css/react-datetime.css";

const StyledLabel = styled.label``;
const StyledHelpText = styled.span``;
const StyledInputs = styled.span``;
const StyledInput = styled(Datetime)`
  .rdtPicker {
    width: calc(100% + 2px);
    margin-top: 0px;
    margin-left: -1px;
    background-color: ${style.white};
    border: 1px solid ${style.black100};
    box-shadow: 0px 3px 2px rgba(0, 35, 44, 0.05);

    @media (max-width: ${style.collapse}px) {
      width: ${({ $type }) =>
        $type === "date" ? "250px" : "calc(100% + 2px)"};
    }
  }
`;
const StyledIcon = styled.span``;
const StyledError = styled.span``;

const StyledField = styled.div`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
  grid-gap: 4px 0.75rem;
  margin-bottom: 0;
  align-items: stretch;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;

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
    height: 40px;
    font-size: 1rem;
    padding: 0;

    input,
    input:focus {
      margin: 0;
      padding: 0.5rem;
      border: none;
      outline: none;
      width: 100%;
      height: 100%;
    }

    &:last-child {
      padding-right: ${({ $invalid }) => ($invalid ? "2.25rem" : "0")};
    }

    &:focus {
      border-color: ${({ $invalid }) =>
        $invalid ? style.redNSP : style.black1000};
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
  const date = moment(datetime).isValid() ? moment(datetime) : moment();
  return {
    date: date.format("DD/MM/YYYY"),
    time: date.format("HH:mm"),
  };
};

const stringifyDatetime = (datetime) => {
  return moment(
    datetime.date + " " + datetime.time,
    "DD/MM/YYYY HH:mm"
  ).format();
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
    dateFieldProps,
    timeFieldProps,
    ...rest
  } = props;
  const parsedValue = useMemo(() => parseDatetime(value), [value]);
  const [time, setTime] = useState(parsedValue.time);
  const [date, setDate] = useState(parsedValue.date);

  const handleChangeDate = useCallback(
    (value) => {
      const isValid = typeof value !== "string";
      value = isValid ? value.format("DD/MM/YYYY") : value;
      setDate(value);
      isValid && onChange && onChange(stringifyDatetime({ date: value, time }));
    },
    [onChange, time]
  );

  const handleChangeTime = useCallback(
    (value) => {
      const isValid = typeof value !== "string";
      value = isValid ? value.format("HH:mm") : value;
      setTime(value);
      isValid && onChange && onChange(stringifyDatetime({ date, time: value }));
    },
    [onChange, date]
  );

  useEffect(() => {
    if (!value) {
      onChange && onChange(stringifyDatetime(parseDatetime(value)));
    } else {
      const newValue = parseDatetime(value);
      setDate(newValue.date);
      setTime(newValue.time);
    }
  }, [value, onChange]);

  return (
    <StyledField $valid={!error} $invalid={!!error} $empty={!!value}>
      {label && <StyledLabel htmlFor={id}>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledInputs>
        {type.includes("date") ? (
          <StyledInput
            $type="date"
            locale="fr"
            inputProps={rest}
            {...dateFieldProps}
            onChange={handleChangeDate}
            value={date}
            dateFormat="DD/MM/YYYY"
            timeFormat={false}
          />
        ) : null}
        {type.includes("time") ? (
          <StyledInput
            $type="time"
            locale="fr"
            inputProps={rest}
            {...timeFieldProps}
            onChange={handleChangeTime}
            value={time}
            timeFormat="HH:mm"
            dateFormat={false}
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
  dateFieldProps: PropTypes.object,
  timeFieldProps: PropTypes.object,
};

DateTimeField.defaultProps = {
  type: "datetime",
};

export default DateTimeField;
