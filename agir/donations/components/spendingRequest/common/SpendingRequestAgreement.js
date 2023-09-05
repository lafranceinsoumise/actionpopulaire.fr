import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import CheckboxField from "@agir/front/formComponents/CheckboxField";

const AgreementField = ({ onChange, disabled, reset }) => {
  const [agreements, setAgreements] = useState({
    political: false,
    legal: false,
  });

  const handleChangeAgreement = (e) => {
    setAgreements((state) => ({
      ...state,
      [e.target.name]: e.target.checked,
    }));
  };

  const hasAgreement = Object.values(agreements).every(Boolean);

  useEffect(() => {
    reset &&
      setAgreements((data) =>
        Object.keys(data).reduce((obj, key) => {
          obj[key] = false;
          return obj;
        }, {})
      );
  }, [reset]);

  useEffect(() => {
    onChange(hasAgreement);
  }, [onChange, hasAgreement]);

  return (
    <>
      <CheckboxField
        disabled={disabled}
        id="political"
        name="political"
        value={agreements.political}
        onChange={handleChangeAgreement}
        label="Je certifie que cette dépense est conforme à la charte des groupes d’action, aux principes, aux orientations politiques, stratégiques, programmatiques et électorales de la France Insoumise. "
      />
      <CheckboxField
        disabled={disabled}
        id="legal"
        name="legal"
        value={agreements.legal}
        onChange={handleChangeAgreement}
        label="Je certifie sur l'honneur être une personne physique et la dépense ne porte pas atteinte à la législation encadrant l’activité des partis et groupements politiques."
      />
    </>
  );
};

AgreementField.propTypes = {
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  reset: PropTypes.bool,
};

export default AgreementField;
