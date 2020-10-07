import React from "react";

import InputRange from "./InputRange";

export default {
  component: InputRange,
  title: "InputRange",
  argTypes: { onChange: { action: "changed" } },
};

const Controller = (props) => {
  const [value, setValue] = React.useState(props.value);

  React.useEffect(() => setValue(props.value), [props.value]);

  return (
    <InputRange
      {...props}
      value={value}
      onChange={(v) => {
        setValue(v);
        props.onChange(v);
      }}
    />
  );
};
Controller.propTypes = InputRange.propTypes;

const Template = (args) => <InputRange {...args} />;

export const Default = Template.bind({});
Default.args = {
  value: 40,
  minValue: 0,
  maxValue: 100,
  step: 1,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};

export const Controlled = (args) => <Controller {...args} />;
Controller.args = {
  ...Default.args,
  value: 50,
};
