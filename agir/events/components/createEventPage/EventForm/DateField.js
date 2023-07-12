import moment from "moment";
import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";
import { DateTime } from "luxon";
import "moment/locale/fr";

import DateTimeField from "@agir/front/formComponents/DateTimeField";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
import SelectField from "@agir/front/formComponents/SelectField";
import TimezoneField from "@agir/front/formComponents/TimezoneField";

import { EVENT_DEFAULT_DURATIONS } from "@agir/events/common/utils";

const TimezoneToggle = styled.p`
  display: flex;
  margin: 0;
  padding-left: 1rem;
  padding-bottom: 0.25rem;
  flex-flow: column nowrap;
  justify-content: flex-end;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.5;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: row;
    padding-left: 0;
    padding-bottom: 0;
  }

  span,
  button,
  button:hover,
  button:focus {
    margin: 0;
    padding: 0;
    background-color: transparent;
    outline: none;
    border: none;
    text-align: left;
  }

  button {
    color: ${(props) => props.theme.primary500};
    cursor: pointer;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin-left: 0.5rem;
    }
  }
`;

const ErrorMessage = styled.p`
  color: ${(props) => props.theme.redNSP};
`;

const Field = styled.div`
  display: inline-grid;
  grid-template-columns: auto 160px 270px;
  grid-auto-rows: auto auto;
  grid-gap: 0.5rem;
  align-items: start;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: grid;
    grid-template-columns: 1fr;
  }
`;

const getDuration = (startTime, endTime) => {
  if (!startTime || !endTime) {
    return EVENT_DEFAULT_DURATIONS[0];
  }

  let startDate = new Date(startTime);
  startDate = DateTime.fromJSDate(startDate);

  let endDate = new Date(endTime);
  endDate = DateTime.fromJSDate(endDate);

  return (
    EVENT_DEFAULT_DURATIONS.find(
      ({ value }) => value === (endDate.ts - startDate.ts) / 60000,
    ) || EVENT_DEFAULT_DURATIONS[EVENT_DEFAULT_DURATIONS.length - 1]
  );
};

const DateField = (props) => {
  const {
    onChange,
    onChangeTimezone,
    startTime,
    endTime,
    timezone,
    error,
    required,
    disabled,
    className,
    showTimezone = false,
  } = props;

  const [hasTimezone, setHasTimezone] = useState(showTimezone);
  const [duration, setDuration] = useState(undefined);
  const inlineError = useResponsiveMemo(error, "");

  const updateStartTime = useCallback(
    (startTime) => {
      let start = moment(startTime);
      let end = moment(endTime);
      if (start.isAfter(end)) {
        end = moment(startTime);
      }
      if (duration && duration.value) {
        end = moment(startTime).add(duration.value, "minutes");
      }
      start = start.format();
      end = end.format();
      onChange(start, end);
    },
    [endTime, duration, onChange],
  );

  const updateEndTime = useCallback(
    (endTime, duration) => {
      let start = moment(startTime);
      let end = moment(endTime);
      if (start.isAfter(end)) {
        start = moment(endTime);
      }
      start = start.format();
      end = end.format();
      duration && setDuration(duration);
      onChange(start, end);
    },
    [startTime, onChange],
  );

  const updateDuration = useCallback(
    (duration) => {
      if (duration && duration.value) {
        updateEndTime(
          moment(startTime).add(duration.value, "minutes"),
          duration,
        );
      } else {
        setDuration(duration);
      }
    },
    [startTime, updateEndTime],
  );

  useEffect(() => {
    !duration &&
      startTime &&
      endTime &&
      setDuration(getDuration(startTime, endTime));
  }, [duration, startTime, endTime]);

  return (
    <>
      <Field className={className}>
        <div>
          <DateTimeField
            label={`Date et heure ${!duration?.value ? "de début" : ""}`.trim()}
            value={startTime}
            onChange={updateStartTime}
            error={inlineError ? inlineError : error ? " " : error}
            required={required}
            disabled={disabled}
          />
        </div>
        <div>
          <SelectField
            label="Durée"
            value={duration?.value ? duration : EVENT_DEFAULT_DURATIONS[4]}
            onChange={updateDuration}
            options={EVENT_DEFAULT_DURATIONS}
            disabled={disabled}
          />
        </div>
        {hasTimezone ? (
          <TimezoneField
            label="Fuseau horaire"
            value={timezone}
            onChange={onChangeTimezone}
            disabled={disabled}
            required={required}
          />
        ) : (
          <TimezoneToggle>
            <span>Fuseau horaire local</span>
            <button type="button" onClick={() => setHasTimezone(true)}>
              Personnaliser
            </button>
          </TimezoneToggle>
        )}
        {!duration?.value && (
          <div>
            <DateTimeField
              label="Date et heure de fin"
              value={endTime}
              onChange={updateEndTime}
              disabled={disabled}
              required={required}
            />
          </div>
        )}
      </Field>
      <ErrorMessage>{error}</ErrorMessage>
    </>
  );
};
DateField.propTypes = {
  onChange: PropTypes.func.isRequired,
  onChangeTimezone: PropTypes.func.isRequired,
  timezone: PropTypes.string,
  startTime: PropTypes.string,
  endTime: PropTypes.string,
  error: PropTypes.string,
  className: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
  showTimezone: PropTypes.bool,
};
export default DateField;
