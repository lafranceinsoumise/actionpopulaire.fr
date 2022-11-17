import React, { useState } from "react";

import CustomField from "@agir/donations/common/CustomField";

import TextField from "@agir/front/formComponents/TextField";
import CountryField from "@agir/front/formComponents/CountryField";

export default {
  component: CustomField,
  title: "Donations/CustomField",
};

const TemplateTextField = (args) => {
  const [formData, setFormData] = useState({ value: "" });

  const handleChange = (e) => {
    setFormData((formData) => ({ ...formData, value: e.target.value }));
  };

  return (
    <CustomField {...args} value={formData.value} onChange={handleChange} />
  );
};

const TemplateCountryField = (args) => {
  const [formData, setFormData] = useState({ country: "FR" });

  const handleChangeCountry = (country) => {
    setFormData((formData) => ({ ...formData, country: country }));
  };

  return (
    <CustomField
      {...args}
      value={formData.country}
      onChange={handleChangeCountry}
    />
  );
};

export const Default = TemplateTextField.bind({});
Default.args = {
  id: 42,
  Component: TextField,
  label: "Nom",
  name: "lastName",
  helpText: "Dites en plus sur vous",
};

export const WithCountryField = TemplateCountryField.bind({});
WithCountryField.args = {
  id: 42,
  Component: CountryField,
  label: "Pays",
  name: "country",
  helpText:
    "Pour savoir où l'on va il est intéressant de savoir d'où l'on vient",
};
