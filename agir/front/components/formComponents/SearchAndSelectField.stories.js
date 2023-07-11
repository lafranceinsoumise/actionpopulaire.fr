import React, { useState, useCallback } from "react";

import SearchAndSelectField from "./SearchAndSelectField";

import TIMEZONES from "./timezones";

export default {
  component: SearchAndSelectField,
  title: "Form/SearchAndSelectField",
  argTypes: {
    onChange: { table: { disable: true } },
    children: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = useState(args.value);
  const [options, setOptions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const handleChange = useCallback((value) => {
    setValue(value);
    setOptions(defaultOptions);
  }, []);

  const handleSearch = useCallback(
    async (q) =>
      await new Promise((resolve) => {
        setIsLoading(true);
        setTimeout(() => {
          setIsLoading(false);
          let options = [];
          if (!q) {
            options = defaultOptions;
          } else {
            options = defaultOptions.filter((option) => {
              return option.label.toLowerCase().includes(q.toLowerCase());
            });
          }
          setOptions(options);
          resolve(options);
        }, 500);
      }),
    [],
  );

  return (
    <div
      style={{
        boxSizing: "border-box",
        padding: "32px 16px",
        maxWidth: "480px",
        margin: "0 auto",
      }}
    >
      <SearchAndSelectField
        {...args}
        value={value}
        onChange={handleChange}
        onSearch={handleSearch}
        isLoading={isLoading}
        defaultOptions={options}
      />
      <pre>
        Value:{" "}
        {value ? (
          <strong>{JSON.stringify(value, null, "\r  ")}</strong>
        ) : (
          <em>empty</em>
        )}
      </pre>
    </div>
  );
};

const defaultOptions = TIMEZONES.map((tz) => ({ label: tz, value: tz }));

export const Default = Template.bind({});
Default.args = {
  value: "",
  placeholder: "Choisir un fuseau horaire",
  type: "text",
  id: "timezone",
  label: "Fuseau horaire",
  error: "",
  disabled: false,
  defaultOptions,
  isLoading: false,
  minSearchTermLength: 1,
};

export const Empty = Default;

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: defaultOptions[0],
};

export const Loading = Template.bind({});
Loading.args = {
  ...Filled.args,
  isLoading: true,
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
