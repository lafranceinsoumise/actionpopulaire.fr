import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { Calendar, DateObject } from "react-multi-date-picker";
import DatePanel from "react-multi-date-picker/plugins/date_panel";
import TimePicker from "react-multi-date-picker/plugins/time_picker";
import styled from "styled-components";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
import { getIconDataUrl } from "@agir/front/genericComponents/Button/utils";

import gregorian_en from "react-date-object/locales/gregorian_en";

const StyledHelpText = styled.p`
  color: ${(props) => props.theme.text700};
  font-size: 0.75rem;
  text-align: left;
  padding: 1rem;
  margin: 0;
  border-top: 1px solid ${(props) => props.theme.text100};
  text-align: center;

  & + & {
    color: ${(props) => props.theme.error500};
  }
`;

const StyledCalendar = styled(Calendar)`
  clear: both;
  border-radius: 0;
  border: 1px solid ${(props) => props.theme.text100};
  box-shadow: none !important;

  /* CALENDAR */

  .rmdp-week-day {
    color: ${(props) => props.theme.primary500};
  }

  .rmdp-day {
    width: 40px;
    height: 40px;

    &.rmdp-deactive {
      color: ${(props) => props.theme.primary600};
    }
    &.rmdp-today span,
    &.rmdp-today span:hover {
      color: ${(props) => props.theme.primary500};
      background-color: transparent;
      font-weight: 700;
    }
    &.rmdp-selected span.highlight,
    &.rmdp-selected span:not(.highlight) {
      color: ${(props) =>
        props.disabled ? props.theme.text1000 : props.theme.background0};
      background-color: ${(props) =>
        props.disabled ? props.theme.primary150 : props.theme.primary500};
      box-shadow: none;
    }
    &.rmdp-selected span.highlight {
      box-shadow: 0 0 0 3px ${(props) => props.theme.primary150};
    }
    &:not(.rmdp-day-hidden) span:hover {
      background-color: ${(props) =>
        props.disabled ? "transparent" : props.theme.primary600} !important;
      color: ${(props) =>
        props.disabled
          ? props.theme.text1000
          : props.theme.background0} !important;
    }
    &.rmdp-today:not(.rmdp-day-hidden) span:hover {
      color: ${(props) =>
        props.disabled
          ? props.theme.primary500
          : props.theme.background0} !important;
    }
    &.rmdp-selected:not(.rmdp-day-hidden) span:hover {
      background-color: ${(props) => props.theme.primary150} !important;
      color: ${(props) => props.theme.primary600};
    }
  }

  .rmdp-range {
    background-color: ${(props) => props.theme.primary500};
    box-shadow: none;
  }

  .rmdp-arrow-container {
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      background-color: ${(props) => props.theme.primary500};
      box-shadow: none;
    }
  }

  .rmdp-arrow {
    margin: 0;
    border: solid ${(props) => props.theme.primary500};
    border-width: 0 2px 2px 0;
  }

  /* TIME PICKER */
  .rmdp-time-picker {
    justify-content: center;

    & > * {
      flex: 0 0 auto;
    }

    & > div input {
      padding: 0;
      width: 4rem;
    }
  }

  /* DATE LIST */
  .rmdp-rtl .rmdp-panel {
    border-left: unset;
    border-right: 1px solid ${(props) => props.theme.primary600};
  }
  .rmdp-panel-header:empty {
    display: none;
  }

  .rmdp-panel {
    & > div {
      position: static !important;
      height: auto !important;
    }
  }

  .rmdp-panel-body {
    margin: 0;
    padding: 0.5rem;
    position: static;

    &::-webkit-scrollbar-thumb {
      background: ${(props) => props.theme.primary500};
    }

    li {
      box-shadow: none;
      align-items: stretch;
      overflow: hidden;
      gap: 0.25rem;
      background-color: transparent;
      border-radius: 0.25rem;

      .b-date {
        background-color: ${(props) => props.theme.primary100};
        color: ${(props) => props.theme.text1000};
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        text-align: left;
        font-weight: 400;
        flex: 1 1 auto;
        margin: 0;

        &:focus,
        &:hover {
          background-color: ${(props) => props.theme.primary150};
        }
      }

      &.last-selected-day .b-date {
        border-left: 0.5rem solid ${(props) => props.theme.primary150};
        font-weight: 500;

        &:focus,
        &:hover {
          border-color: ${(props) => props.theme.primary500};
        }
      }

      & > .b-deselect {
        position: static;
        display: block;
        height: unset;
        flex: 0 0 40px;
        transform: none;
        border-radius: 0;
        color: transparent;
        line-height: normal;
        background-color: ${(props) => props.theme.text100};
        background-image: ${(props) =>
          getIconDataUrl({
            color: props.theme.text1000,
          })({
            icon: "trash-2",
          })};
        background-size: 1rem 1rem;
        background-repeat: no-repeat;
        background-position: center center;

        &:focus,
        &:hover {
          background-color: ${(props) => props.theme.text200};
        }
      }
    }
  }
  .rmdp-panel-disabled {
    .rmdp-panel-body {
      li {
        & > .b-deselect {
          display: none;
        }
      }
    }
  }
`;

const locale = {
  ...gregorian_en,
  name: "gregorian_fr",
  months: [
    ["Janvier", "Janv"],
    ["Février", "Fevr"],
    ["Mars", "Mars"],
    ["Avril", "Avr"],
    ["Mai", "Mai"],
    ["Juin", "Juin"],
    ["Juillet", "Juil"],
    ["Août", "Août"],
    ["Septembre", "Sept"],
    ["Octobre", "Oct"],
    ["Novembre", "Nov"],
    ["Décembre", "Déc"],
  ],
  weekDays: [
    ["Samedi", "S"],
    ["Dimanche", "D"],
    ["Lundi", "L"],
    ["Mardi", "M"],
    ["Mercredi", "M"],
    ["Jeudi", "J"],
    ["Vendredi", "V"],
  ],
};

const convertIsoDateOffset = (date) => {
  const [splitDate, offset] = date.split("+");

  if (!offset || offset.indexOf(":") >= 0) {
    return date;
  }

  const hoursOffset = offset.substring(0, 2) || "00";
  const secondsOffset = offset.substring(2, 4) || "00";

  return `${splitDate}+${hoursOffset}:${secondsOffset}`;
};

const getInitialValue = (value) => {
  if (!value) {
    return null;
  }
  return value
    .split(",")
    .map(
      (v) =>
        new DateObject(
          new Date(v.length === 10 ? v + " 00:00:00" : convertIsoDateOffset(v)),
        ),
    )
    .filter((v) => v.isValid);
};

const LengthHelpText = (props) => {
  const { min, max, current } = props;
  if (!min || !max) {
    return null;
  }
  let text = "";
  if (!current) {
    text += "Veuillez sélectionner ";
    if (min && max && min !== max) {
      text += `entre ${min} et ${max} dates`;
    } else if (min === max) {
      text += `${max} dates`;
    } else if (min) {
      text += `minimum ${min} date${min > 1 ? "s" : ""}`;
    } else {
      text += `${max} date${max > 1 ? "s" : ""} maximum`;
    }
  } else {
    text += `${current}${max ? `/${max}` : ""} date${
      current > 1 ? "s" : ""
    } sélectionnée${current > 1 ? "s" : ""}`;
  }
  return <StyledHelpText>{text}</StyledHelpText>;
};
LengthHelpText.propTypes = {
  min: PropTypes.number,
  max: PropTypes.number,
  current: PropTypes.number,
};

const MultiDateInput = (props) => {
  const {
    initialValue,
    onChange,
    id,
    name,
    helpText,
    error,
    format = "YYYY-MM-DD HH:mm:ss",
    minDate,
    maxDate,
    minLength = 1,
    maxLength,
    className,
    disabled,
    readOnly,
  } = props;

  const calendarMonths = useResponsiveMemo(1, 2);
  const [value, setValue] = useState(getInitialValue(initialValue));
  const [focusedDate, setFocusedDate] = useState();

  const hasTime = useMemo(() => format.toUpperCase().includes("HH"), [format]);

  const DateList = useMemo(
    () => (
      <DatePanel
        sort="date"
        position="bottom"
        formatFunction={(date) =>
          date.date.format(`DD MMMM YYYY${hasTime ? " — HH:mm" : ""}`)
        }
        markFocused
        focusedClassName="last-selected-day"
        className={disabled || readOnly ? "rmdp-panel-disabled" : ""}
      />
    ),
    [readOnly, disabled, hasTime],
  );

  const TimeInput = useMemo(
    () => (
      <TimePicker
        key="time-picker"
        position="bottom"
        disabled={disabled || readOnly}
        hideSeconds
      />
    ),
    [readOnly, disabled],
  );

  const initialDate = useMemo(
    () =>
      new DateObject((value && value[0]) || minDate || undefined).set({
        hour: 18,
        minute: 0,
        second: 0,
      }),
    [value, minDate],
  );

  const outputValue = useMemo(
    () =>
      value
        ? value
            .map((dateObject) =>
              hasTime
                ? // Cast dateObject to UTC string with datetimes
                  dateObject.toDate().toISOString().split(".")[0] + "Z"
                : dateObject.format(format),
            )
            .join(",")
        : "",
    [value, format, hasTime],
  );

  const handleChange = useCallback(
    (value) => {
      Array.isArray(value) && maxLength
        ? setValue(value.slice(0, maxLength))
        : setValue(value);
    },
    [maxLength],
  );

  const mapDays = useCallback(
    ({ date, isSameDate }) =>
      isSameDate(date, focusedDate) ? { className: "highlight" } : undefined,
    [focusedDate],
  );

  return (
    <StyledCalendar
      multiple
      currentDate={initialDate}
      weekStartDayIndex={1}
      numberOfMonths={calendarMonths}
      locale={locale}
      format={format}
      minDate={minDate}
      maxDate={maxDate}
      value={value}
      onChange={handleChange}
      onFocusedDateChange={setFocusedDate}
      disabled={disabled}
      readOnly={readOnly}
      className={className}
      plugins={[
        hasTime && TimeInput,
        value && value.length > 0 && DateList,
      ].filter(Boolean)}
      shadow={false}
      mapDays={mapDays}
    >
      <input
        id={id}
        name={name}
        type="hidden"
        value={outputValue}
        onChange={onChange}
      />
      <LengthHelpText
        min={minLength}
        max={maxLength}
        current={value?.length || 0}
      />
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      {error && <StyledHelpText>{error}</StyledHelpText>}
    </StyledCalendar>
  );
};

MultiDateInput.propTypes = {
  onChange: PropTypes.func,
  initialValue: PropTypes.string,
  id: PropTypes.string,
  name: PropTypes.string,
  helpText: PropTypes.node,
  error: PropTypes.string,
  format: PropTypes.string,
  minDate: PropTypes.string,
  maxDate: PropTypes.string,
  minLength: PropTypes.number,
  maxLength: PropTypes.number,
  minDelta: PropTypes.number,
  maxDelta: PropTypes.number,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  readOnly: PropTypes.bool,
};

export default MultiDateInput;
