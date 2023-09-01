import React from "react";

import AttachmentModal from "./AttachmentModal";

export default {
  component: AttachmentModal,
  title: "Donations/SpendingRequest/AttachmentModal",
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
      <AttachmentModal {...args} value={value} onChange={handleChange} />
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
  value: null,
  id: "field",
  label: "Pièces-jointes",
  error: "",
  disabled: false,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Default.args,
  value: {
    type: "I",
    title: "Le ticket de caisse",
    file: {
      name: "ticket.pdf",
    },
  },
};

export const WithValidationError = Template.bind({});
WithValidationError.args = {
  ...Filled.args,
  error: {
    global: "Texte d’erreur générique",
    type: "Vous avez triché avec un type qui n'existe même pas !",
    title: "Ce nom ne fonctionne pas !",
    file: "Le format est inutilisable !",
  },
};

export const Loading = Template.bind({});
Loading.args = {
  ...Filled.args,
  isLoading: true,
};
