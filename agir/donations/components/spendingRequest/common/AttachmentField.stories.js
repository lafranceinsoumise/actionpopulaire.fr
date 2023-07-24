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
  value: [],
  id: "field",
  label: "Pièces-jointes",
  error: "",
  disabled: false,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Default.args,
  value: [
    {
      type: "I",
      title: "Le ticket de caisse",
      file: {
        name: "ticket.pdf",
      },
    },
    {
      type: "P",
      title: "Photo de la salle des fêtes",
      file: "https://loremflickr.com/255/130",
    },
  ],
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
