import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import { useHistory, useRouteMatch } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import SubtypePanel from "@agir/events/common/SubtypePanel";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { getEventSubtypeInfo } from "@agir/events/common/utils";
import { routeConfig } from "@agir/front/app/routes.config";

const StyledDefaultOption = styled.button``;
const StyledPanelTrigger = styled.button``;
const StyledHelp = styled.div``;

export const StyledDefaultOptions = styled.div`
  display: flex;
  flex-flow: row wrap;
  gap: 0.5rem;

  ${StyledDefaultOption},
  ${StyledPanelTrigger} {
    border-radius: ${style.borderRadius};
    border: none;
    box-shadow: none;
    padding: 0;
    background-color: transparent;
    font-size: 1rem;
    font-weight: 400;
    cursor: pointer;
    color: ${style.primary500};

    &[disabled],
    &[disabled]:hover {
      opacity: 0.5;
      cursor: default;
    }
  }

  ${StyledDefaultOption} {
    padding: 0.5rem 0.75rem;
    color: ${style.black1000};
    display: inline-grid;
    grid-gap: 0.5rem;
    grid-template-columns: auto auto auto;
    align-items: center;
    border: 1px solid ${style.black100};

    &:hover {
      background-color: ${style.black50};
    }

    &[disabled],
    &[disabled]:hover {
      opacity: 1;
      background-color: transparent;
      cursor: default;
    }
  }

  ${StyledPanelTrigger} {
    font-weight: 500;
  }

  ${StyledHelp} {
    flex: 0 0 100%;
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    line-height: 1.5;
    color: ${style.black500};

    & > * {
      flex: 1 1 auto;
      line-height: 1.5;
    }

    & > ${RawFeatherIcon} {
      flex: 0 0 auto;
      line-height: 0;
    }
  }
`;

const StyledField = styled.div`
  label {
    font-size: 1rem;
    font-weight: 600;
    line-height: 1;
    padding: 4px 0;
  }
`;

export const DefaultOption = (props) => {
  const { option, onClick, selected, disabled } = props;

  const handleClick = useCallback(() => {
    onClick(option);
  }, [option, onClick]);

  return (
    <StyledDefaultOption
      type="button"
      title={option.description}
      color="choose"
      onClick={handleClick}
      disabled={disabled}
    >
      <RawFeatherIcon
        name={selected ? "check" : "circle"}
        width="1rem"
        height="1rem"
      />
      <span
        className={`fa fa-${option.iconName || "calendar"}`}
        style={{ color: option.color }}
      />
      {option.description && (
        <>
          {option.description[0].toUpperCase()}
          {option.description.slice(1)}
        </>
      )}
    </StyledDefaultOption>
  );
};
DefaultOption.propTypes = {
  option: PropTypes.shape({
    id: PropTypes.number,
    label: PropTypes.string,
    iconName: PropTypes.string,
    color: PropTypes.string,
    description: PropTypes.string,
  }),
  onClick: PropTypes.func,
  selected: PropTypes.bool,
  disabled: PropTypes.bool,
};

const BASE_ROUTE = routeConfig.createEvent.getLink();
const PANEL_ROUTE = BASE_ROUTE + "type/";

const SubtypeField = (props) => {
  const { onChange, value, name, error, disabled, options, lastUsedIds } =
    props;

  const isPanelOpen = useRouteMatch(PANEL_ROUTE);
  const history = useHistory();

  const openPanel = useCallback(() => {
    history.push(PANEL_ROUTE);
  }, [history]);

  const closePanel = useCallback(() => {
    history.replace(BASE_ROUTE);
  }, [history]);

  const handleChange = useCallback(
    (subtype) => {
      onChange(name, subtype);
      closePanel();
    },
    [onChange, name, closePanel]
  );

  const subtypes = useMemo(() => {
    if (!Array.isArray(options)) {
      return [];
    }

    return options;
  }, [options]);

  const defaultOptions = useMemo(() => subtypes.slice(0, 5), [subtypes]);
  const info = getEventSubtypeInfo(value);

  return (
    <StyledField>
      <label htmlFor={name}>Type d'événement</label>
      {error && (
        <p
          style={{
            color: style.redNSP,
            fontSize: "0.813rem",
          }}
        >
          {error}
        </p>
      )}
      <StyledDefaultOptions>
        {value ? (
          <DefaultOption
            key={value.id}
            option={value}
            onClick={openPanel}
            selected
          />
        ) : (
          defaultOptions.map((subtype) => (
            <DefaultOption
              key={subtype.id}
              onClick={handleChange}
              option={subtype}
              disabled={disabled}
            />
          ))
        )}
        {(!!value || (!value && subtypes.length > 4)) && (
          <StyledPanelTrigger
            onClick={openPanel}
            type="button"
            disabled={disabled}
          >
            {value ? "Modifier" : "+ d'options"}
          </StyledPanelTrigger>
        )}
        {!!info && (
          <StyledHelp>
            <RawFeatherIcon name="info" width="1.5rem" height="1.5rem" />
            <span>
              {info
                .split("\n")
                .reduce((all, cur) => [...all, <br key={cur} />, cur])}
            </span>
          </StyledHelp>
        )}
      </StyledDefaultOptions>
      <SubtypePanel
        onClose={closePanel}
        onChange={handleChange}
        value={value}
        options={subtypes}
        lastUsedIds={lastUsedIds}
        shouldShow={!!isPanelOpen}
      />
    </StyledField>
  );
};
SubtypeField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.object,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.object),
  lastUsedIds: PropTypes.arrayOf(PropTypes.number),
  error: PropTypes.string,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
};
export default SubtypeField;
