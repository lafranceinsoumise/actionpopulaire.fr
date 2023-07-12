import { DateTime } from "luxon";
import React from "react";

import TimezoneField from "./TimezoneField";
import DateTimeField from "./DateTimeField";

export default {
  component: TimezoneField,
  title: "Form/TimezoneField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((timezone) => {
    setValue(timezone);
  }, []);

  return (
    <div
      style={{
        boxSizing: "border-box",
        padding: "32px 16px",
        maxWidth: "480px",
        margin: "0 auto",
      }}
    >
      <TimezoneField {...args} value={value} onChange={handleChange} />
      <pre>Value : {value ? <strong>{value}</strong> : <em>empty</em>}</pre>
    </div>
  );
};

export const Empty = Template.bind({});
Empty.args = {
  value: "",
  name: "timezone",
  label: "Fuseau horaire",
  error: "",
  maxLength: undefined,
  disabled: false,
  textArea: false,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: "Europe/Paris",
};

export const WithHelpText = Template.bind({});
WithHelpText.args = {
  ...Filled.args,
  helpText: "Texte d'aide si necessaire",
};

export const Focused = Template.bind({});
Focused.args = {
  ...Filled.args,
  autoFocus: true,
};

export const WithValidationError = Template.bind({});
WithValidationError.args = {
  ...Filled.args,
  error: "Texte d’erreur sur le champ",
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Filled.args,
  disabled: true,
};

export const WithDateTimeField = (args = Filled.args) => {
  const [tz, setTz] = React.useState(
    args.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone,
  );
  const [value, setValue] = React.useState(args.value);
  const [timezonedValue, setTimezonedValue] = React.useState();

  const handleChangeTz = React.useCallback((tz) => {
    setTz(tz);
  }, []);

  const handleChangeDate = React.useCallback((datetime) => {
    setValue(datetime);
  }, []);

  React.useEffect(() => {
    if (value && tz) {
      const timezonedValue = DateTime.fromISO(value)
        .setZone(tz, { keepLocalTime: true })
        .toISO();
      setTimezonedValue(timezonedValue);
    }
  }, [tz, value]);

  return (
    <div
      style={{
        boxSizing: "border-box",
        padding: "32px 16px",
        maxWidth: "480px",
        margin: "0 auto",
      }}
    >
      <DateTimeField {...args} value={value} onChange={handleChangeDate} />
      <TimezoneField {...args} value={tz} onChange={handleChangeTz} />
      <pre>
        Value :{" "}
        {timezonedValue ? (
          <>
            <strong>{timezonedValue}</strong>
            &nbsp;
            <small>({tz})</small>
          </>
        ) : (
          <em>empty</em>
        )}
      </pre>
      <button onClick={() => setValue(args.value)}>Reset</button>
    </div>
  );
};
