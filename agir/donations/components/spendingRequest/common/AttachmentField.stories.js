import React from "react";

import AttachmentField from "./AttachmentField";

export default {
  component: AttachmentField,
  title: "Donations/SpendingRequest/AttachmentField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((value) => {
    setValue(value);
  }, []);

  return (
    <div>
      <AttachmentField {...args} value={value} onChange={handleChange} />
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

export const Default = Template.bind({});
Default.args = {
  value: "",
  id: "field",
  label: "Image",
  error: "",
  disabled: false,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Default.args,
  initialValue: {
    type: "I",
    title: "La facture",
    file: "file.png",
  },
};

export const WithValidationError = Template.bind({});
WithValidationError.args = {
  ...Filled.args,
  error: {
    title: "Texte d’erreur sur le champ",
    type: "Texte d’erreur sur le champ",
    file: "Texte d’erreur sur le champ",
  },
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Filled.args,
  disabled: true,
};
