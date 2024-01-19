import React, { useEffect, useState } from "react";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import TextField from "@agir/front/formComponents/TextField";
import styled from "styled-components";

import { useEventFormOptions } from "@agir/events/common/hooks";

const StyledField = styled.div`
  > span:first-child {
    font-size: 1rem;
    font-weight: 600;
    line-height: 1;
    padding: 4px 0;
  }
`;

const OnlineUrlField = (props) => {
  const {
    id,
    name,
    label,
    placeholder,
    value,
    onChange,
    error,
    disabled,
    ...rest
  } = props;

  const options = useEventFormOptions();
  const defaultUrl = options.onlineUrl;
  const [isOnline, setIsOnline] = useState(!!value);
  const [onlineUrl, setOnlineUrl] = useState(value);
  const [isAuto, setIsAuto] = useState(false);

  useEffect(() => {
    setIsOnline(!!value);
    setOnlineUrl(value);
  }, [value]);

  const handleChange = (e) => {
    onChange(name, e.target.value);
  };

  const handleChangeUrl = (event) => {
    if (!event.target.checked) {
      setIsAuto(false);
      return;
    }
    onChange(name, defaultUrl);
    setIsAuto(true);
  };

  const handleChangeOnline = (event) => {
    setIsOnline(event.target.checked);
    if (!event.target.checked) {
      onChange(name, "");
      return;
    }
  };

  return (
    <StyledField>
      <span>{label}</span>
      <CheckboxField
        disabled={disabled}
        label="Se déroule en ligne"
        value={isOnline}
        onChange={handleChangeOnline}
      />
      {isOnline && (
        <>
          {!!defaultUrl && (
            <CheckboxField
              disabled={disabled}
              label="Utiliser le service de visio-conférence automatique de La France insoumise"
              value={isAuto && onlineUrl === defaultUrl}
              onChange={handleChangeUrl}
            />
          )}
          <TextField
            {...rest}
            label=""
            disabled={disabled}
            name="url"
            error={error}
            value={onlineUrl}
            onChange={handleChange}
            placeholder={placeholder}
            maxLength={2000}
            hasCounter={false}
          />
        </>
      )}
    </StyledField>
  );
};

export default OnlineUrlField;
